from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class JournalEntry(models.Model):
    MOOD_CHOICES = [
        ('😊', 'Happy'),
        ('😢', 'Sad'),
        ('😠', 'Angry'),
        ('😴', 'Tired'),
        ('😃', 'Excited'),
        ('😌', 'Peaceful'),
        ('😕', 'Confused'),
        ('🤔', 'Thoughtful'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_created = models.DateTimeField(default=timezone.now)
    date_modified = models.DateTimeField(auto_now=True)
    mood = models.CharField(max_length=2, choices=MOOD_CHOICES, default='😊')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-date_created']
        verbose_name_plural = 'Journal Entries'
    
    def __str__(self):
        return f"{self.title} - {self.date_created.strftime('%Y-%m-%d')}"
    
    def get_absolute_url(self):
        return reverse('entry_detail', kwargs={'pk': self.pk})