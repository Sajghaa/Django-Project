from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import markdown
from bleach import clean

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:category_posts', args=[self.slug])

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True, max_length=500)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    featured_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.published_at:
            return reverse('blog:post_detail', args=[self.published_at.year, 
                                                      self.published_at.month, 
                                                      self.published_at.day, 
                                                      self.slug])
        return reverse('blog:post_detail', args=[2024, 1, 1, self.slug])  # Fallback

    def get_markdown_content(self):
        """Convert markdown content to HTML"""
        extensions = [
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
            'markdown.extensions.smarty',
        ]
        html = markdown.markdown(self.content, extensions=extensions)
        # Sanitize HTML to prevent XSS
        allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'ul', 'ol', 'li', 'a', 'pre', 'code', 'blockquote', 'img', 'table',
            'thead', 'tbody', 'tr', 'th', 'td', 'hr', 'div', 'span'
        ]
        allowed_attributes = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'title'],
            'code': ['class'],
            'pre': ['class'],
            'div': ['class'],
            'span': ['class'],
        }
        return clean(html, tags=allowed_tags, attributes=allowed_attributes, strip=False)

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.post.title}'