from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid

class TimeStampedModel(models.Model):
    """Abstract base model with timestamp fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

class Subscriber(TimeStampedModel):
    """Model for newsletter subscribers"""
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('unsubscribed', 'Unsubscribed'),
        ('bounced', 'Bounced'),
        ('pending', 'Pending Confirmation'),
    ]
    
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmation_token = models.UUIDField(default=uuid.uuid4, unique=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Preferences
    receive_newsletter = models.BooleanField(default=True)
    receive_promotions = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Subscriber'
        verbose_name_plural = 'Subscribers'
    
    def __str__(self):
        return self.email
    
    def confirm_subscription(self):
        """Confirm the subscription"""
        self.status = 'active'
        self.confirmed_at = timezone.now()
        self.save()
    
    def unsubscribe(self):
        """Unsubscribe from newsletter"""
        self.status = 'unsubscribed'
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def send_confirmation_email(self):
        """Send confirmation email"""
        subject = 'Confirm Your Newsletter Subscription'
        confirmation_url = f"{settings.SITE_URL}/newsletter/confirm/{self.confirmation_token}/"
        
        print(f"Sending confirmation email to {self.email}")
        print(f"Confirmation URL: {confirmation_url}")

class Newsletter(TimeStampedModel):
    """Model for newsletters"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]
    
    subject = models.CharField(max_length=200)
    content = models.TextField()
    html_content = models.TextField(blank=True, help_text="HTML version of the newsletter")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_for = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Recipients
    sent_to_count = models.IntegerField(default=0)
    opened_count = models.IntegerField(default=0)
    clicked_count = models.IntegerField(default=0)
    
    # Tracking
    track_opens = models.BooleanField(default=True)
    track_clicks = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Newsletter'
        verbose_name_plural = 'Newsletters'
    
    def __str__(self):
        return self.subject

class NewsletterClick(models.Model):
    """Track newsletter link clicks"""
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='clicks')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    url = models.URLField()
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Newsletter Click'
        verbose_name_plural = 'Newsletter Clicks'

class NewsletterOpen(models.Model):
    """Track newsletter opens"""
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='opens')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    opened_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Newsletter Open'
        verbose_name_plural = 'Newsletter Opens'