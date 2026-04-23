from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import markdown

class Notebook(models.Model):
    """Notebook for organizing notes"""
    
    COLOR_CHOICES = (
        ('default', 'Default'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
        ('purple', 'Purple'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notebooks')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='default')
    icon = models.CharField(max_length=50, default='fas fa-book')
    note_count = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.name

class Tag(models.Model):
    """Tag for labeling notes"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default='secondary')
    note_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
    
    def __str__(self):
        return self.name

class Note(models.Model):
    """Note model for storing user notes"""
    
    COLOR_CHOICES = (
        ('default', 'Default'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('red', 'Red'),
        ('purple', 'Purple'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    notebook = models.ForeignKey(Notebook, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    content = models.TextField(blank=True)
    content_html = models.TextField(blank=True, editable=False)
    summary = models.CharField(max_length=500, blank=True)
    
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='default')
    is_favorite = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_trash = models.BooleanField(default=False)
    pinned = models.BooleanField(default=False)
    order_position = models.IntegerField(default=0)
    
    view_count = models.PositiveIntegerField(default=0)
    reminder_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-pinned', '-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'notebook']),
            models.Index(fields=['user', 'is_trash']),
            models.Index(fields=['user', 'is_favorite']),
        ]
    
    def save(self, *args, **kwargs):
        # Generate slug
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Note.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        # Generate summary from content
        if self.content and not self.summary:
            # Simple text stripping for summary
            plain_content = self.content.replace('\n', ' ').replace('#', '').replace('*', '')
            self.summary = plain_content[:200] + '...' if len(plain_content) > 200 else plain_content
        
        # Convert markdown to HTML
        if self.content:
            self.content_html = markdown.markdown(
                self.content,
                extensions=['extra', 'codehilite', 'nl2br']
            )
        
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Soft delete the note"""
        self.is_trash = True
        self.deleted_at = timezone.now()
        self.save()
    
    def restore(self):
        """Restore from trash"""
        self.is_trash = False
        self.deleted_at = None
        self.save()
    
    def __str__(self):
        return self.title

class Attachment(models.Model):
    """File attachments for notes"""
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=200)
    file_size = models.PositiveIntegerField()
    file_type = models.CharField(max_length=100)
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.filename

class NoteShare(models.Model):
    """Public sharing for notes"""
    
    note = models.OneToOneField(Note, on_delete=models.CASCADE, related_name='share')
    share_token = models.CharField(max_length=100, unique=True, blank=True)
    share_password = models.CharField(max_length=255, blank=True, null=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def generate_token(self):
        import uuid
        return uuid.uuid4().hex
    
    def save(self, *args, **kwargs):
        if not self.share_token:
            self.share_token = self.generate_token()
        super().save(*args, **kwargs)
    
    def is_valid(self):
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

class NoteVersion(models.Model):
    """Version history for notes"""
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='versions')
    title = models.CharField(max_length=200)
    content = models.TextField()
    version_number = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-version_number']
    
    def __str__(self):
        return f"Version {self.version_number} of {self.note.title}"