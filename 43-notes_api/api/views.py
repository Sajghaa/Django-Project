from rest_framework import viewsets, status, generics, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.db.models import Q
from django.shortcuts import get_object_or_404
from .models import Notebook, Tag, Note, Attachment, NoteShare, NoteVersion
from .serializers import (
    UserSerializer, NotebookSerializer, TagSerializer,
    NoteListSerializer, NoteDetailSerializer, NoteCreateUpdateSerializer,
    AttachmentSerializer, NoteShareSerializer, NoteVersionSerializer
)
from .permissions import IsOwnerOrReadOnly, IsNotebookOwner, IsTagOwner, CanViewSharedNote
from .pagination import CustomPagination
from .filters import NoteFilter, NotebookFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data.get('email', ''),
            password=request.data.get('password')
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

class NotebookViewSet(viewsets.ModelViewSet):
    """ViewSet for notebooks"""
    queryset = Notebook.objects.none()  # Will be filtered by get_queryset
    serializer_class = NotebookSerializer
    permission_classes = [IsAuthenticated, IsNotebookOwner]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NotebookFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'note_count']
    ordering = ['name']
    
    def get_queryset(self):
        return Notebook.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """Get all notes in this notebook"""
        notebook = self.get_object()
        notes = Note.objects.filter(notebook=notebook, is_trash=False)
        page = self.paginate_queryset(notes)
        serializer = NoteListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for tags"""
    queryset = Tag.objects.none()  # Will be filtered by get_queryset
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated, IsTagOwner]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'note_count']
    ordering = ['name']
    
    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """Get all notes with this tag"""
        tag = self.get_object()
        notes = Note.objects.filter(tags=tag, is_trash=False)
        page = self.paginate_queryset(notes)
        serializer = NoteListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for notes"""
    queryset = Note.objects.none()  # Will be filtered by get_queryset
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = NoteFilter
    search_fields = ['title', 'content']
    ordering_fields = ['updated_at', 'created_at', 'title', 'view_count']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)
        
        # Filter out trash unless specifically requested
        if not self.request.query_params.get('is_trash'):
            queryset = queryset.filter(is_trash=False)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return NoteCreateUpdateSerializer
        else:
            return NoteDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def favorite(self, request, pk=None):
        """Toggle favorite status"""
        note = self.get_object()
        note.is_favorite = not note.is_favorite
        note.save()
        return Response({'is_favorite': note.is_favorite})
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Toggle archive status"""
        note = self.get_object()
        note.is_archived = not note.is_archived
        note.save()
        return Response({'is_archived': note.is_archived})
    
    @action(detail=True, methods=['post'])
    def pin(self, request, pk=None):
        """Toggle pin status"""
        note = self.get_object()
        note.pinned = not note.pinned
        note.save()
        return Response({'pinned': note.pinned})
    
    @action(detail=True, methods=['post'])
    def trash(self, request, pk=None):
        """Move note to trash"""
        note = self.get_object()
        note.soft_delete()
        return Response({'is_trash': True})
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore note from trash"""
        note = self.get_object()
        note.restore()
        return Response({'is_trash': False})
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get version history"""
        note = self.get_object()
        versions = note.versions.all()
        serializer = NoteVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """Increment view count"""
        note = self.get_object()
        note.view_count += 1
        note.save()
        return Response({'view_count': note.view_count})
    
    @action(detail=True, methods=['post', 'delete'])
    def share(self, request, pk=None):
        """Create or delete share link"""
        note = self.get_object()
        
        if request.method == 'POST':
            share, created = NoteShare.objects.get_or_create(note=note)
            serializer = NoteShareSerializer(share, data=request.data, partial=True, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            if request.data.get('share_password'):
                from django.contrib.auth.hashers import make_password
                share.share_password = make_password(request.data['share_password'])
            if request.data.get('expires_at'):
                share.expires_at = request.data['expires_at']
            share.save()
            
            return Response(NoteShareSerializer(share, context={'request': request}).data)
        
        else:  # DELETE
            if hasattr(note, 'share'):
                note.share.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['post'])
    def attachments(self, request, pk=None):
        """Upload attachment"""
        note = self.get_object()
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        attachment = Attachment.objects.create(
            note=note,
            file=uploaded_file,
            filename=uploaded_file.name,
            file_size=uploaded_file.size,
            file_type=uploaded_file.name.split('.')[-1].lower(),
            mime_type=uploaded_file.content_type
        )
        
        serializer = AttachmentSerializer(attachment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PublicNoteView(generics.RetrieveAPIView):
    """Public view for shared notes"""
    queryset = Note.objects.all()
    serializer_class = NoteDetailSerializer
    permission_classes = [AllowAny, CanViewSharedNote]
    lookup_field = 'share_token'
    
    def get_object(self):
        share_token = self.kwargs.get('share_token')
        share = get_object_or_404(NoteShare, share_token=share_token)
        
        # Check password if required
        if share.share_password:
            password = self.request.query_params.get('password')
            from django.contrib.auth.hashers import check_password
            if not password or not check_password(password, share.share_password):
                self.permission_denied(self.request, message="Password required")
        
        # Increment view count
        share.view_count += 1
        share.save()
        
        return share.note

class SearchView(generics.ListAPIView):
    """Advanced search endpoint"""
    serializer_class = NoteListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        notes = Note.objects.filter(user=self.request.user, is_trash=False)
        
        if query:
            notes = notes.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        return notes