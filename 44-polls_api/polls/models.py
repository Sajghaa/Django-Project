from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify

class Poll(models.Model):
    """Poll/Survey model"""
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    allow_multiple_votes = models.BooleanField(default=False)
    require_auth = models.BooleanField(default=False)
    
    total_responses = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_active', 'start_date', 'end_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Poll.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def is_open(self):
        """Check if poll is currently open for voting"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date and now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
    
    def __str__(self):
        return self.title

class Question(models.Model):
    """Question model for polls"""
    
    QUESTION_TYPES = (
        ('single', 'Single Choice'),
        ('multiple', 'Multiple Choice'),
        ('text', 'Text Answer'),
    )
    
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default='single')
    is_required = models.BooleanField(default=True)
    order_position = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_position']
    
    def __str__(self):
        return self.text[:50]

class Choice(models.Model):
    """Choice option for multiple choice questions"""
    
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    order_position = models.IntegerField(default=0)
    vote_count = models.PositiveIntegerField(default=0)
    allow_custom = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_position']
    
    def __str__(self):
        return self.text

class Response(models.Model):
    """Poll response (one submission per user)"""
    
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='poll_responses')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Response to {self.poll.title} at {self.submitted_at}"

class Vote(models.Model):
    """Individual vote for a question"""
    
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='votes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True, related_name='votes')
    text_answer = models.TextField(blank=True)  # For text type questions
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.choice:
            return f"{self.question.text[:30]}: {self.choice.text}"
        return f"{self.question.text[:30]}: {self.text_answer[:30]}"