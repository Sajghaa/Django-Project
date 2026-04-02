from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
import string

class User(AbstractUser):
    """Custom User Model with additional fields"""
    
    # Personal Information
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Address Information
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    
    # Social Links
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    # Account Status
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    reset_password_token = models.CharField(max_length=100, blank=True)
    reset_password_token_created = models.DateTimeField(null=True, blank=True)
    
    # Activity Tracking
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    account_created_at = models.DateTimeField(auto_now_add=True)
    account_updated_at = models.DateTimeField(auto_now=True)
    
    def generate_verification_token(self):
        """Generate email verification token"""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        self.email_verification_token = token
        self.save()
        return token
    
    def generate_reset_token(self):
        """Generate password reset token"""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        self.reset_password_token = token
        self.reset_password_token_created = timezone.now()
        self.save()
        return token
    
    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'