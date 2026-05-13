from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import uuid

class Channel(models.Model):
    """YouTube channel model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='channel')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    subscribers = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-subscribers']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    """Video category"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fas fa-video')
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Video(models.Model):
    """Video model"""
    
    PRIVACY_CHOICES = (
        ('public', 'Public'),
        ('unlisted', 'Unlisted'),
        ('private', 'Private'),
    )
    
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='videos')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='videos')
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    duration = models.PositiveIntegerField(default=0, help_text="Duration in seconds")
    
    views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    dislikes = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default='public')
    allow_comments = models.BooleanField(default=True)
    allow_likes = models.BooleanField(default=True)
    
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['channel', '-published_at']),
            models.Index(fields=['category', '-published_at']),
            models.Index(fields=['views', '-published_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Video.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_formatted_duration(self):
        """Return duration in MM:SS format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    """Video comments"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(max_length=10000)
    likes = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.video.title}"

class VideoLike(models.Model):
    """Video likes/dislikes"""
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='likes_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_likes')
    value = models.IntegerField(default=1)  # 1 for like, -1 for dislike
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['video', 'user']
    
    def __str__(self):
        return f"{self.user.username} {'liked' if self.value == 1 else 'disliked'} {self.video.title}"

class Subscription(models.Model):
    """Channel subscriptions"""
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE, related_name='subscribers_info')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['subscriber', 'channel']
    
    def __str__(self):
        return f"{self.subscriber.username} subscribed to {self.channel.name}"

class Playlist(models.Model):
    """User playlists"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    video_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'slug']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"

class PlaylistVideo(models.Model):
    """Videos in playlists"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name='videos_info')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='in_playlists')
    order_position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['playlist', 'video']
        ordering = ['order_position']
    
    def __str__(self):
        return f"{self.video.title} in {self.playlist.name}"

class WatchHistory(models.Model):
    """User watch history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watch_history')
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='watch_history')
    watched_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0, help_text="Percentage watched")
    
    class Meta:
        unique_together = ['user', 'video']
        ordering = ['-watched_at']
    
    def __str__(self):
        return f"{self.user.username} watched {self.video.title}"