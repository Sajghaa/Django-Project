from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Image, ProcessedImage

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        return data

class ProcessedImageSerializer(serializers.ModelSerializer):
    url_full = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessedImage
        fields = ['id', 'size_type', 'width', 'height', 'filename', 'file_size', 'url', 'url_full', 'created_at']
        read_only_fields = ['id', 'filename', 'file_size', 'created_at']
    
    def get_url_full(self, obj):
        request = self.context.get('request')
        if obj.url and request:
            return request.build_absolute_uri(obj.url)
        return None

class ImageSerializer(serializers.ModelSerializer):
    processed_versions = ProcessedImageSerializer(many=True, read_only=True)
    url_full = serializers.SerializerMethodField()
    original_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Image
        fields = ['id', 'original_name', 'filename', 'file_size', 'file_type',
                  'width', 'height', 'format', 'url', 'url_full', 'original_url',
                  'processed_versions', 'created_at']
        read_only_fields = ['id', 'filename', 'file_size', 'created_at']
    
    def get_url_full(self, obj):
        request = self.context.get('request')
        if obj.url and request:
            return request.build_absolute_uri(obj.url)
        return None
    
    def get_original_url(self, obj):
        request = self.context.get('request')
        if obj.url and request:
            return request.build_absolute_uri(obj.url)
        return None

class ImageUploadSerializer(serializers.Serializer):
    image = serializers.ImageField()
    width = serializers.IntegerField(required=False, min_value=50, max_value=4096)
    height = serializers.IntegerField(required=False, min_value=50, max_value=4096)
    maintain_aspect = serializers.BooleanField(default=True)
    quality = serializers.IntegerField(default=85, min_value=1, max_value=100)
    format = serializers.ChoiceField(choices=['JPEG', 'PNG', 'WEBP'], required=False)
    generate_thumbnails = serializers.BooleanField(default=False)

class ImageResizeSerializer(serializers.Serializer):
    width = serializers.IntegerField(required=False, min_value=50, max_value=4096)
    height = serializers.IntegerField(required=False, min_value=50, max_value=4096)
    maintain_aspect = serializers.BooleanField(default=True)
    quality = serializers.IntegerField(default=85, min_value=1, max_value=100)
    format = serializers.ChoiceField(choices=['JPEG', 'PNG', 'WEBP'], required=False)

class ImageFilterSerializer(serializers.Serializer):
    filter_type = serializers.ChoiceField(choices=[
        'grayscale', 'blur', 'sharpen', 'sepia'
    ])
    intensity = serializers.IntegerField(default=50, min_value=0, max_value=100, required=False)

class ImageAdjustSerializer(serializers.Serializer):
    adjustment_type = serializers.ChoiceField(choices=['brightness', 'contrast'])
    factor = serializers.FloatField(min_value=0.0, max_value=2.0)

class ImageRotateSerializer(serializers.Serializer):
    angle = serializers.IntegerField(min_value=0, max_value=360)

class ImageCropSerializer(serializers.Serializer):
    left = serializers.IntegerField(min_value=0)
    top = serializers.IntegerField(min_value=0)
    right = serializers.IntegerField(min_value=0)
    bottom = serializers.IntegerField(min_value=0)

class BatchUploadSerializer(serializers.Serializer):
    images = serializers.ListField(child=serializers.ImageField())
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)