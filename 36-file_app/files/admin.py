from django.contrib import admin
from .models import File, FileDownload

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'uploaded_by', 'file_size', 'access_type', 'download_count', 'created_at']
    list_filter = ['access_type', 'is_active', 'created_at']
    search_fields = ['original_name', 'title', 'uploaded_by__username']
    readonly_fields = ['file_hash', 'download_count', 'created_at', 'updated_at']

@admin.register(FileDownload)
class FileDownloadAdmin(admin.ModelAdmin):
    list_display = ['file', 'user', 'ip_address', 'downloaded_at']
    list_filter = ['downloaded_at']
    search_fields = ['file__original_name', 'user__username']