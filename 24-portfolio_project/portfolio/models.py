from django.db import models
from django.utils.text import slugify
from django.utils import timezone
import random
import string

class Skill(models.Model):
    class SkillLevel(models.TextChoices):
        BEGINNER = 'Beginner', 'Beginner'
        INTERMEDIATE = 'Intermediate', 'Intermediate'
        ADVANCED = 'Advanced', 'Advanced'
        EXPERT = 'Expert', 'Expert'
    
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=SkillLevel.choices, default=SkillLevel.INTERMEDIATE)
    percentage = models.IntegerField(help_text="Skill proficiency percentage (0-100)", default=50)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class", blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Portfolio(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='portfolios')
    description = models.TextField()
    technologies = models.CharField(max_length=500, help_text="Comma-separated technologies used")
    image = models.ImageField(upload_to='portfolio/')
    image_alt = models.CharField(max_length=200, blank=True)
    project_url = models.URLField(blank=True, help_text="Live project URL")
    github_url = models.URLField(blank=True, help_text="GitHub repository URL")
    client = models.CharField(max_length=200, blank=True)
    completion_date = models.DateField(default=timezone.now)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-featured', '-completion_date']
        verbose_name_plural = 'Portfolios'
    
    def generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        while Portfolio.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{''.join(random.choices(string.digits, k=4))}"
        return slug
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Service(models.Model):
    title = models.CharField(max_length=200)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title

class Testimonial(models.Model):
    name = models.CharField(max_length=200)
    position = models.CharField(max_length=200)
    company = models.CharField(max_length=200, blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating = models.IntegerField(default=5, help_text="Rating out of 5")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.company}"

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(help_text="Short summary of the post")
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/')
    author = models.CharField(max_length=100, default='Admin')
    read_time = models.IntegerField(help_text="Estimated reading time in minutes", default=5)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    views = models.IntegerField(default=0)
    published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def generate_unique_slug(self):
        base_slug = slugify(self.title)
        slug = base_slug
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{''.join(random.choices(string.digits, k=4))}"
        return slug
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.subject}"

class SiteInfo(models.Model):
    site_name = models.CharField(max_length=200, default='My Portfolio')
    site_tagline = models.CharField(max_length=200, default='Creative Developer & Designer')
    site_description = models.TextField(default='Welcome to my portfolio')
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    favicon = models.ImageField(upload_to='site/', blank=True, null=True)
    email = models.EmailField(default='hello@myportfolio.com')
    phone = models.CharField(max_length=20, default='+1 234 567 8900')
    address = models.TextField(default='123 Creative Street, Digital City')
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    about_text = models.TextField(default='Write about yourself here')
    hero_title = models.CharField(max_length=200, default='I Create Amazing Digital Experiences')
    hero_subtitle = models.CharField(max_length=200, default='Creative Developer & Designer')
    hero_image = models.ImageField(upload_to='site/', blank=True, null=True)
    resume_file = models.FileField(upload_to='site/', blank=True, null=True)
    
    def __str__(self):
        return self.site_name
    
    class Meta:
        verbose_name_plural = 'Site Info'