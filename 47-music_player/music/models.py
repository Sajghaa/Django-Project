from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Genre(models.Model):
    """Music genre/category"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fas fa-music')
    song_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Artist(models.Model):
    """Music artist/band"""
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='artists/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='artists/covers/', blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    monthly_listeners = models.PositiveIntegerField(default=0)
    followers_count = models.PositiveIntegerField(default=0)
    songs_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-monthly_listeners', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    """Music album"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='albums')
    cover_image = models.ImageField(upload_to='albums/', blank=True, null=True)
    release_date = models.DateField()
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    song_count = models.PositiveIntegerField(default=0)
    total_duration = models.PositiveIntegerField(default=0, help_text="Total duration in seconds")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-release_date']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} by {self.artist.name}"

class Song(models.Model):
    """Individual song/track"""
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='songs')
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True, blank=True, related_name='songs')
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True, blank=True)
    duration = models.PositiveIntegerField(help_text="Duration in seconds")
    audio_file = models.FileField(upload_to='songs/')
    cover_art = models.ImageField(upload_to='songs/covers/', blank=True, null=True)
    lyrics = models.TextField(blank=True)
    release_date = models.DateField()
    play_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-play_count', '-created_at']
        indexes = [
            models.Index(fields=['artist', '-play_count']),
            models.Index(fields=['genre', '-play_count']),
            models.Index(fields=['-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Song.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Update album and artist counts
        if self.album:
            self.album.song_count = self.album.songs.count()
            self.album.save()
        
        self.artist.songs_count = self.artist.songs.count()
        self.artist.save()
        
        if self.genre:
            self.genre.song_count = Song.objects.filter(genre=self.genre).count()
            self.genre.save()
        
        super().save(*args, **kwargs)
    
    def get_formatted_duration(self):
        """Return duration in MM:SS format"""
        minutes = self.duration // 60
        seconds = self.duration % 60
        return f"{minutes}:{seconds:02d}"
    
    def __str__(self):
        return f"{self.title} by {self.artist.name}"

class Playlist(models.Model):
    """User-created playlist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    name = models.CharField(max_length=200)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='playlists/', blank=True, null=True)
    songs = models.ManyToManyField(Song, through='PlaylistSong', related_name='playlists')
    is_public = models.BooleanField(default=True)
    song_count = models.PositiveIntegerField(default=0)
    total_duration = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'slug']
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} by {self.user.username}"

class PlaylistSong(models.Model):
    """Ordered songs in playlist"""
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    order_position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_position']
        unique_together = ['playlist', 'song']
    
    def __str__(self):
        return f"{self.song.title} in {self.playlist.name}"

class UserFavorite(models.Model):
    """User's liked/favorite songs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'song']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} liked {self.song.title}"

class ListeningHistory(models.Model):
    """User's listening history"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listening_history')
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='listened_by')
    played_at = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0, help_text="Percentage completed")
    
    class Meta:
        ordering = ['-played_at']
    
    def __str__(self):
        return f"{self.user.username} played {self.song.title} at {self.played_at}"

class ArtistFollow(models.Model):
    """User follows artist"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followed_artists')
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'artist']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} follows {self.artist.name}"