from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

class Category(models.Model):
    """Task category"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20, default='primary')
    icon = models.CharField(max_length=50, default='fas fa-tag')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Project(models.Model):
    """Project for grouping tasks"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=20, default='primary')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Task(models.Model):
    """Task model with deadlines and priorities"""
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
        ('cancelled', 'Cancelled'),
    )
    
    # Basic Information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Organization
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    
    # Priority & Status
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority_score = models.IntegerField(default=0)
    
    # Dates
    due_date = models.DateTimeField()
    completed_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    
    # Time Tracking
    estimated_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    actual_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_rule = models.JSONField(null=True, blank=True)
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    
    # Metadata
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    attachment = models.FileField(upload_to='task_attachments/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority_score', 'due_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'status', 'due_date']),
            models.Index(fields=['user', 'priority_score']),
        ]
    
    def save(self, *args, **kwargs):
        # Calculate priority score before saving
        self.priority_score = self.calculate_priority_score()
        
        # Set started_at when status changes to in_progress
        if self.status == 'in_progress' and not self.started_at:
            self.started_at = timezone.now()
        
        # Set completed_at when status changes to completed
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def calculate_priority_score(self):
        """Calculate priority score based on urgency and time remaining"""
        score = 0
        
        # Priority weight (0-40 points)
        priority_weights = {
            'urgent': 40,
            'high': 30,
            'medium': 20,
            'low': 10,
        }
        score += priority_weights.get(self.priority, 0)
        
        # Time remaining weight (0-40 points)
        if self.due_date:
            now = timezone.now()
            if self.due_date < now:
                # Overdue tasks get highest priority
                score += 50
            else:
                hours_remaining = (self.due_date - now).total_seconds() / 3600
                if hours_remaining < 24:
                    score += 40
                elif hours_remaining < 72:
                    score += 30
                elif hours_remaining < 168:
                    score += 20
                else:
                    score += 10
        
        return score
    
    def is_overdue(self):
        """Check if task is overdue"""
        if self.status == 'completed':
            return False
        return self.due_date and self.due_date < timezone.now()
    
    def get_priority_display_with_icon(self):
        """Get priority with icon"""
        icons = {
            'urgent': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢',
        }
        return f"{icons.get(self.priority, '')} {self.get_priority_display()}"
    
    def __str__(self):
        return self.title

class Subtask(models.Model):
    """Subtask for breaking down main tasks"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    title = models.CharField(max_length=200)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    order_index = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order_index']
    
    def save(self, *args, **kwargs):
        if self.is_completed and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Reminder(models.Model):
    """Reminders for tasks"""
    REMINDER_TYPES = (
        ('email', 'Email'),
        ('push', 'Push Notification'),
        ('both', 'Both'),
    )
    
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='reminders')
    reminder_time = models.DateTimeField()
    reminder_type = models.CharField(max_length=10, choices=REMINDER_TYPES, default='email')
    is_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Reminder for {self.task.title} at {self.reminder_time}"

class TaskHistory(models.Model):
    """Track task changes"""
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)
    old_value = models.TextField(blank=True)
    new_value = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.action} - {self.task.title} at {self.created_at}"