from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os
import uuid

def get_image_upload_path(instance, filename):
    """Generate unique filename for uploaded images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', filename)

def get_processed_path(instance, filename):
    """Generate unique filename for processed images"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('processed', filename)

class Image(models.Model):
    """Original uploaded image"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    original_name = models.CharField(max_length=500)
    filename = models.CharField(max_length=500, unique=True)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=100)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    format = models.CharField(max_length=10)
    url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.original_name

class ProcessedImage(models.Model):
    """Processed/resized version of original image"""
    
    SIZE_TYPES = (
        ('original', 'Original'),
        ('thumbnail', 'Thumbnail'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('custom', 'Custom'),
    )
    
    original_image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name='processed_versions')
    size_type = models.CharField(max_length=20, choices=SIZE_TYPES, default='custom')
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    filename = models.CharField(max_length=500, unique=True)
    file_size = models.PositiveIntegerField()
    url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.original_image.original_name} - {self.width}x{self.height}"