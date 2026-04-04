from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from .managers import CustomUserManager
import random
import string

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model with email as username field
    """
    
    # Account Types
    ACCOUNT_TYPES = (
        ('user', 'Regular User'),
        ('premium', 'Premium User'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    )
    
    # Basic Information
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=50, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    
    # Personal Information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Address
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Social Links
    website = models.URLField(blank=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    
    # Account Settings
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Email Verification
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Password Reset
    reset_password_token = models.CharField(max_length=100, blank=True)
    reset_password_token_created = models.DateTimeField(null=True, blank=True)
    
    # Two-Factor Authentication (2FA)
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=100, blank=True)
    
    # Login Tracking
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Preferences
    language = models.CharField(max_length=10, default='en')
    timezone = models.CharField(max_length=50, default='UTC')
    email_notifications = models.BooleanField(default=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.username or self.email
    
    def get_short_name(self):
        return self.first_name or self.username or self.email.split('@')[0]
    
    def generate_verification_token(self):
        """Generate email verification token"""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        self.email_verification_token = token
        self.email_verification_sent_at = timezone.now()
        self.save()
        return token
    
    def generate_reset_token(self):
        """Generate password reset token"""
        token = ''.join(random.choices(string.ascii_letters + string.digits, k=64))
        self.reset_password_token = token
        self.reset_password_token_created = timezone.now()
        self.save()
        return token
    
    def is_token_valid(self, token_type='reset'):
        """Check if token is still valid (24 hours)"""
        if token_type == 'reset':
            token_time = self.reset_password_token_created
        else:
            token_time = self.email_verification_sent_at
        
        if token_time:
            time_diff = timezone.now() - token_time
            return time_diff.total_seconds() < 86400  # 24 hours
        return False
    
    def increment_login_attempts(self):
        """Increment failed login attempts"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save()
    
    def reset_login_attempts(self):
        """Reset login attempts after successful login"""
        self.login_attempts = 0
        self.locked_until = None
        self.save()
    
    def is_locked(self):
        """Check if account is locked"""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    @property
    def is_premium(self):
        return self.account_type == 'premium'

class LoginHistory(models.Model):
    """Track user login history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    successful = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-login_time']
        verbose_name_plural = 'Login Histories'
    
    def __str__(self):
        return f"{self.user.email} - {self.login_time}"