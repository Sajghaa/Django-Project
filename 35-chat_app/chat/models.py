from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import random
import string

class ChatRoom(models.Model):
    """Chat room model"""
    ROOM_TYPES = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('direct', 'Direct Message'),
    )
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES, default='public')
    participants = models.ManyToManyField(User, related_name='chat_rooms', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure unique slug
            original_slug = self.slug
            counter = 1
            while ChatRoom.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('chat:room', kwargs={'slug': self.slug})
    
    @property
    def participant_count(self):
        return self.participants.count()
    
    @property
    def message_count(self):
        return self.messages.count()

class Message(models.Model):
    """Chat message model"""
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(max_length=5000)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"
    
    @property
    def time_ago(self):
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} hours ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} minutes ago"
        else:
            return "Just now"

class UserProfile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=100, default='Online', blank=True)
    last_seen = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def update_last_seen(self):
        self.last_seen = timezone.now()
        self.save()

class UserStatus(models.Model):
    """Track user online/offline status"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='status')
    is_online = models.BooleanField(default=False)
    last_activity = models.DateTimeField(default=timezone.now)
    current_room = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Online' if self.is_online else 'Offline'}"