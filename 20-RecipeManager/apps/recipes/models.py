from django.db import models
from django.conf import settings
from django.urls import reverse
from taggit.managers import TaggableManager

class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField(help_text="List all ingredients, one per line")
    instructions = models.TextField(help_text="Step by step instructions")
    prep_time = models.IntegerField(help_text="Preparation time in minutes")
    cook_time = models.IntegerField(help_text="Cooking time in minutes")
    servings = models.IntegerField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    image = models.ImageField(upload_to='recipes/', null=True, blank=True)
    
    # Relationships
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recipes')
    tags = TaggableManager(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('recipes:detail', kwargs={'pk': self.pk})
    
    @property
    def total_time(self):
        return self.prep_time + self.cook_time