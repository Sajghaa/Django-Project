from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Image, ProcessedImage
from .serializers import (
    UserSerializer, RegisterSerializer, ImageSerializer, ProcessedImageSerializer,
    ImageUploadSerializer, ImageResizeSerializer, ImageFilterSerializer,
    ImageAdjustSerializer, ImageRotateSerializer, ImageCropSerializer, BatchUploadSerializer
)
from .processors import ImageProcessor
from .pagination import CustomPagination
import os
import uuid
from datetime import datetime

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    """Custom auth token endpoint"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })

class ImageViewSet(viewsets.ModelViewSet):
    """ViewSet for images"""
    queryset = Image.objects.none()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Image.objects.none()
        return Image.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        return ImageSerializer
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """Upload and process image"""
        serializer = ImageUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uploaded_file = serializer.validated_data['image']
        width = serializer.validated_data.get('width')
        height = serializer.validated_data.get('height')
        maintain_aspect = serializer.validated_data['maintain_aspect']
        quality = serializer.validated_data['quality']
        target_format = serializer.validated_data.get('format')
        generate_thumbnails = serializer.validated_data['generate_thumbnails']
        
        # Validate file type
        if uploaded_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
            return Response({'error': 'Invalid file type'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get original image dimensions
        from PIL import Image as PILImage
        import io
        
        pil_image = PILImage.open(uploaded_file)
        original_width, original_height = pil_image.size
        
        # Save original image
        ext = uploaded_file.name.split('.')[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Create image record
        image = Image.objects.create(
            user=request.user,
            original_name=uploaded_file.name,
            filename=filename,
            file_size=uploaded_file.size,
            file_type=uploaded_file.content_type,
            width=original_width,
            height=original_height,
            format=ext.upper(),
            url=f"/media/uploads/{filename}"
        )
        
        # Save file
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Process image if resize requested
        processed_data = None
        if width or height:
            processor = ImageProcessor()
            processed_output, new_width, new_height, img_format = processor.resize_image(
                uploaded_file, width, height, maintain_aspect, quality
            )
            
            # Save processed image
            ext = target_format.lower() if target_format else img_format.lower()
            processed_filename = f"{uuid.uuid4().hex}.{ext}"
            processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', processed_filename)
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            with open(processed_path, 'wb') as f:
                f.write(processed_output.getvalue())
            
            processed_image = ProcessedImage.objects.create(
                original_image=image,
                size_type='custom',
                width=new_width,
                height=new_height,
                filename=processed_filename,
                file_size=processed_output.getbuffer().nbytes,
                url=f"/media/processed/{processed_filename}"
            )
            
            processed_data = ProcessedImageSerializer(processed_image, context={'request': request}).data
            
            # Generate thumbnails if requested
            if generate_thumbnails:
                for size_name, (thumb_width, thumb_height) in settings.THUMBNAIL_SIZES.items():
                    thumb_output, _, _, _ = processor.resize_image(
                        uploaded_file, thumb_width, thumb_height, True, quality
                    )
                    thumb_filename = f"{uuid.uuid4().hex}_{thumb_width}x{thumb_height}.jpg"
                    thumb_path = os.path.join(settings.MEDIA_ROOT, 'thumbnails', thumb_filename)
                    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
                    
                    with open(thumb_path, 'wb') as f:
                        f.write(thumb_output.getvalue())
                    
                    ProcessedImage.objects.create(
                        original_image=image,
                        size_type=size_name,
                        width=thumb_width,
                        height=thumb_height,
                        filename=thumb_filename,
                        file_size=thumb_output.getbuffer().nbytes,
                        url=f"/media/thumbnails/{thumb_filename}"
                    )
        
        response_data = ImageSerializer(image, context={'request': request}).data
        if processed_data:
            response_data['processed'] = processed_data
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def resize(self, request, pk=None):
        """Resize existing image"""
        image = self.get_object()
        serializer = ImageResizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        width = serializer.validated_data.get('width')
        height = serializer.validated_data.get('height')
        maintain_aspect = serializer.validated_data['maintain_aspect']
        quality = serializer.validated_data['quality']
        target_format = serializer.validated_data.get('format')
        
        # Get original file
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.filename)
        
        with open(file_path, 'rb') as f:
            from django.core.files.base import File
            file_obj = File(f)
            
            processor = ImageProcessor()
            processed_output, new_width, new_height, img_format = processor.resize_image(
                file_obj, width, height, maintain_aspect, quality
            )
            
            # Save processed image
            ext = target_format.lower() if target_format else img_format.lower()
            processed_filename = f"{uuid.uuid4().hex}.{ext}"
            processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', processed_filename)
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            with open(processed_path, 'wb') as dest:
                dest.write(processed_output.getvalue())
            
            processed_image = ProcessedImage.objects.create(
                original_image=image,
                size_type='custom',
                width=new_width,
                height=new_height,
                filename=processed_filename,
                file_size=processed_output.getbuffer().nbytes,
                url=f"/media/processed/{processed_filename}"
            )
        
        return Response(ProcessedImageSerializer(processed_image, context={'request': request}).data)
    
    @action(detail=True, methods=['post'])
    def filter(self, request, pk=None):
        """Apply filter to image"""
        image = self.get_object()
        serializer = ImageFilterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        filter_type = serializer.validated_data['filter_type']
        
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.filename)
        
        with open(file_path, 'rb') as f:
            from django.core.files.base import File
            file_obj = File(f)
            
            processor = ImageProcessor()
            
            if filter_type == 'grayscale':
                processed_output = processor.apply_grayscale(file_obj)
            elif filter_type == 'blur':
                intensity = serializer.validated_data.get('intensity', 50)
                radius = max(1, intensity / 20)
                processed_output = processor.apply_blur(file_obj, radius)
            elif filter_type == 'sharpen':
                processed_output = processor.apply_sharpen(file_obj)
            elif filter_type == 'sepia':
                processed_output = processor.apply_sepia(file_obj)
            else:
                return Response({'error': 'Invalid filter type'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Save filtered image
            processed_filename = f"{uuid.uuid4().hex}_filtered.jpg"
            processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', processed_filename)
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            with open(processed_path, 'wb') as dest:
                dest.write(processed_output.getvalue())
            
            # Get dimensions of filtered image
            from PIL import Image as PILImage
            import io
            pil_img = PILImage.open(io.BytesIO(processed_output.getvalue()))
            width, height = pil_img.size
            
            processed_image = ProcessedImage.objects.create(
                original_image=image,
                size_type='custom',
                width=width,
                height=height,
                filename=processed_filename,
                file_size=processed_output.getbuffer().nbytes,
                url=f"/media/processed/{processed_filename}"
            )
        
        return Response(ProcessedImageSerializer(processed_image, context={'request': request}).data)
    
    @action(detail=True, methods=['post'])
    def rotate(self, request, pk=None):
        """Rotate image"""
        image = self.get_object()
        serializer = ImageRotateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        angle = serializer.validated_data['angle']
        
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.filename)
        
        with open(file_path, 'rb') as f:
            from django.core.files.base import File
            file_obj = File(f)
            
            processor = ImageProcessor()
            processed_output = processor.rotate_image(file_obj, angle)
            
            processed_filename = f"{uuid.uuid4().hex}_rotated.jpg"
            processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', processed_filename)
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            with open(processed_path, 'wb') as dest:
                dest.write(processed_output.getvalue())
            
            from PIL import Image as PILImage
            import io
            pil_img = PILImage.open(io.BytesIO(processed_output.getvalue()))
            width, height = pil_img.size
            
            processed_image = ProcessedImage.objects.create(
                original_image=image,
                size_type='custom',
                width=width,
                height=height,
                filename=processed_filename,
                file_size=processed_output.getbuffer().nbytes,
                url=f"/media/processed/{processed_filename}"
            )
        
        return Response(ProcessedImageSerializer(processed_image, context={'request': request}).data)
    
    @action(detail=True, methods=['post'])
    def crop(self, request, pk=None):
        """Crop image"""
        image = self.get_object()
        serializer = ImageCropSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        left = serializer.validated_data['left']
        top = serializer.validated_data['top']
        right = serializer.validated_data['right']
        bottom = serializer.validated_data['bottom']
        
        file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', image.filename)
        
        with open(file_path, 'rb') as f:
            from django.core.files.base import File
            file_obj = File(f)
            
            processor = ImageProcessor()
            processed_output = processor.crop_image(file_obj, left, top, right, bottom)
            
            processed_filename = f"{uuid.uuid4().hex}_cropped.jpg"
            processed_path = os.path.join(settings.MEDIA_ROOT, 'processed', processed_filename)
            os.makedirs(os.path.dirname(processed_path), exist_ok=True)
            
            with open(processed_path, 'wb') as dest:
                dest.write(processed_output.getvalue())
            
            from PIL import Image as PILImage
            import io
            pil_img = PILImage.open(io.BytesIO(processed_output.getvalue()))
            width, height = pil_img.size
            
            processed_image = ProcessedImage.objects.create(
                original_image=image,
                size_type='custom',
                width=width,
                height=height,
                filename=processed_filename,
                file_size=processed_output.getbuffer().nbytes,
                url=f"/media/processed/{processed_filename}"
            )
        
        return Response(ProcessedImageSerializer(processed_image, context={'request': request}).data)