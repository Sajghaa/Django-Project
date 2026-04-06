from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.utils.html import strip_tags
import bleach

class Comment(models.Model):
    """
    Generic comment model that can be attached to any model
    """
    STATUS_CHOICES = (
        ('pending', 'Pending Moderation'),
        ('approved', 'Approved'),
        ('spam', 'Spam'),
        ('deleted', 'Deleted'),
    )
    
    # Generic foreign key to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Comment content
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField(max_length=5000)
    content_html = models.TextField(blank=True, editable=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_edited = models.BooleanField(default=False)
    
    # Moderation
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_comments')
    moderation_note = models.CharField(max_length=500, blank=True)
    moderated_at = models.DateTimeField(null=True, blank=True)
    
    # Engagement
    likes = models.PositiveIntegerField(default=0)
    reports = models.PositiveIntegerField(default=0)
    
    # User info
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['author', 'created_at']),
        ]
    
    def save(self, *args, **kwargs):
        # Sanitize HTML content
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'a', 'code', 'pre', 'ul', 'ol', 'li', 'blockquote']
        allowed_attributes = {'a': ['href', 'title', 'target']}
        
        self.content_html = bleach.clean(
            self.content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        
        if self.pk and Comment.objects.filter(pk=self.pk).exists():
            original = Comment.objects.get(pk=self.pk)
            if original.content != self.content:
                self.is_edited = True
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.content_object}"
    
    @property
    def excerpt(self):
        return strip_tags(self.content_html)[:150] + '...' if len(self.content_html) > 150 else self.content_html
    
    @property
    def reply_count(self):
        return self.replies.filter(status='approved').count()
    
    def approve(self, moderator=None):
        self.status = 'approved'
        if moderator:
            self.moderator = moderator
            self.moderated_at = timezone.now()
        self.save()
    
    def mark_as_spam(self, moderator=None):
        self.status = 'spam'
        if moderator:
            self.moderator = moderator
            self.moderated_at = timezone.now()
        self.save()
    
    def delete_comment(self, moderator=None):
        self.status = 'deleted'
        self.content = '[This comment has been deleted]'
        self.content_html = '<em>This comment has been deleted by a moderator.</em>'
        if moderator:
            self.moderator = moderator
            self.moderated_at = timezone.now()
        self.save()

class CommentLike(models.Model):
    """Track likes on comments"""
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes_info')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'user']
    
    def __str__(self):
        return f"{self.user.username} liked comment {self.comment.id}"

class CommentReport(models.Model):
    """Track user reports on comments"""
    REASON_CHOICES = (
        ('spam', 'Spam or advertising'),
        ('offensive', 'Offensive language'),
        ('harassment', 'Harassment or bullying'),
        ('hate_speech', 'Hate speech'),
        ('misinformation', 'Misinformation'),
        ('other', 'Other'),
    )
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports_info')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_reports')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True, max_length=1000)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'reporter']
    
    def __str__(self):
        return f"{self.reporter.username} reported comment {self.comment.id} for {self.reason}"

class CommentSubscription(models.Model):
    """Users can subscribe to comment threads"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comment_subscriptions')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    subscribed_at = models.DateTimeField(auto_now_add=True)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'content_type', 'object_id']
    
    def __str__(self):
        return f"{self.user.username} subscribed to {self.content_object}"