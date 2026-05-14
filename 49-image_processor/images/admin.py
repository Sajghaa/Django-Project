from django.contrib import admin
from .models import Image, ProcessedImage

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'user', 'width', 'height', 'file_size', 'created_at']
    list_filter = ['format', 'created_at']
    search_fields = ['original_name', 'user__username']
    readonly_fields = ['filename', 'file_size', 'created_at']

@admin.register(ProcessedImage)
class ProcessedImageAdmin(admin.ModelAdmin):
    list_display = ['original_image', 'size_type', 'width', 'height', 'file_size', 'created_at']
    list_filter = ['size_type', 'created_at']
    search_fields = ['original_image__original_name']