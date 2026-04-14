from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os
import hashlib

def get_file_path(instance, filename):
    """Generate unique file path"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', filename)

class File(models.Model):
    """File model for uploaded files"""
    
    ACCESS_CHOICES = (
        ('public', 'Public - Anyone can access'),
        ('private', 'Private - Only me'),
        ('shared', 'Shared - Specific users'),
        ('link', 'Link - Anyone with link'),
    )
    
    # Basic info
    file = models.FileField(upload_to=get_file_path, max_length=500)
    original_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=100, blank=True)
    file_hash = models.CharField(max_length=64, unique=True, blank=True)
    
    # Metadata
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    
    # Ownership
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files')
    
    # Access control
    access_type = models.CharField(max_length=10, choices=ACCESS_CHOICES, default='private')
    allowed_users = models.ManyToManyField(User, blank=True, related_name='shared_files')
    access_code = models.CharField(max_length=20, blank=True, unique=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)  # Hashed password
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    max_downloads = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    download_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['access_code']),
            models.Index(fields=['uploaded_by', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Generate unique access code
        if not self.access_code:
            self.access_code = uuid.uuid4().hex[:12].upper()
        
        # Calculate file size and type
        if self.file and not self.file_size:
            self.file_size = self.file.size
            self.file_type = self.get_file_type()
        
        # Generate file hash
        if self.file and not self.file_hash:
            self.file_hash = self.calculate_file_hash()
        
        super().save(*args, **kwargs)
    
    def get_file_type(self):
        """Get file type from extension"""
        ext = os.path.splitext(self.file.name)[1].lower()
        file_types = {
            '.pdf': 'PDF Document',
            '.doc': 'Word Document',
            '.docx': 'Word Document',
            '.txt': 'Text File',
            '.jpg': 'JPEG Image',
            '.jpeg': 'JPEG Image',
            '.png': 'PNG Image',
            '.gif': 'GIF Image',
            '.zip': 'ZIP Archive',
            '.rar': 'RAR Archive',
            '.xls': 'Excel Spreadsheet',
            '.xlsx': 'Excel Spreadsheet',
        }
        return file_types.get(ext, 'Unknown')
    
    def calculate_file_hash(self):
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        for chunk in self.file.chunks():
            sha256.update(chunk)
        return sha256.hexdigest()
    
    def is_expired(self):
        """Check if file is expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def can_download(self):
        """Check if file can still be downloaded"""
        if not self.is_active:
            return False
        if self.is_expired():
            return False
        if self.max_downloads > 0 and self.download_count >= self.max_downloads:
            return False
        return True
    
    def get_readable_size(self):
        """Get human readable file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} GB"
    
    def __str__(self):
        return self.original_name

class FileDownload(models.Model):
    """Track file downloads"""
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='downloads')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-downloaded_at']
    
    def __str__(self):
        return f"Download of {self.file.original_name} at {self.downloaded_at}"