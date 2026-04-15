from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
import hashlib

class URL(models.Model):
    """Main URL model for shortened links"""
    
    # Basic Info
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=20, unique=True, db_index=True)
    custom_alias = models.CharField(max_length=50, unique=True, null=True, blank=True)
    
    # User Association
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='urls')
    
    # Metadata
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Security
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_clicks = models.PositiveIntegerField(default=0)
    unique_clicks = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_clicked_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['short_code']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def generate_short_code(self, length=6):
        """Generate a random short code"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    def save(self, *args, **kwargs):
        if not self.short_code:
            if self.custom_alias:
                self.short_code = self.custom_alias
            else:
                # Generate unique short code
                for _ in range(5):  # Try up to 5 times
                    code = self.generate_short_code()
                    if not URL.objects.filter(short_code=code).exists():
                        self.short_code = code
                        break
        
        # Set title from original URL if not provided
        if not self.title and self.original_url:
            from urllib.parse import urlparse
            parsed = urlparse(self.original_url)
            self.title = parsed.netloc
        
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if URL has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def can_access(self):
        """Check if URL can be accessed"""
        return self.is_active and not self.is_expired()
    
    def increment_click(self):
        """Increment click count"""
        self.total_clicks += 1
        self.last_clicked_at = timezone.now()
        self.save()
    
    def get_short_url(self):
        """Get full short URL"""
        from django.conf import settings
        return f"{settings.BASE_URL}/{self.short_code}"
    
    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}"

class Click(models.Model):
    """Track individual clicks for analytics"""
    
    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name='clicks')
    
    # Request Info
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(max_length=2000, blank=True, null=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Geo Location
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Device Info
    device_type = models.CharField(max_length=50, blank=True)  # mobile, desktop, tablet
    browser = models.CharField(max_length=50, blank=True)
    operating_system = models.CharField(max_length=50, blank=True)
    
    # Timestamp
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-clicked_at']
        indexes = [
            models.Index(fields=['url', '-clicked_at']),
            models.Index(fields=['ip_address', '-clicked_at']),
        ]
    
    def __str__(self):
        return f"Click on {self.url.short_code} at {self.clicked_at}"

class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    total_links = models.PositiveIntegerField(default=0)
    total_clicks = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_api_key(self):
        """Generate unique API key"""
        import uuid
        self.api_key = uuid.uuid4().hex
        self.save()
        return self.api_key
    
    def __str__(self):
        return f"{self.user.username}'s profile"