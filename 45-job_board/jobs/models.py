from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime
from decimal import Decimal

class Company(models.Model):
    """Company/Employer profile"""
    
    INDUSTRY_CHOICES = (
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    )
    
    SIZE_CHOICES = (
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1000+', '1000+ employees'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    description = models.TextField()
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, default='other')
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    founded_year = models.IntegerField(null=True, blank=True)
    location = models.CharField(max_length=200)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class JobCategory(models.Model):
    """Job categories for organization"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='fas fa-briefcase')
    job_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Job Categories'
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class JobSkill(models.Model):
    """Skills/Tags for jobs"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    job_count = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Job(models.Model):
    """Job posting model"""
    
    EMPLOYMENT_TYPES = (
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
    )
    
    EXPERIENCE_LEVELS = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead'),
        ('executive', 'Executive'),
    )
    
    REMOTE_TYPES = (
        ('remote', 'Fully Remote'),
        ('hybrid', 'Hybrid'),
        ('onsite', 'On-site'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('active', 'Active'),
        ('closed', 'Closed'),
        ('expired', 'Expired'),
    )
    
    # Basic Information
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=200)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, related_name='jobs')
    skills = models.ManyToManyField(JobSkill, blank=True, related_name='jobs')
    
    # Description
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField(blank=True)
    
    # Location
    location = models.CharField(max_length=200)
    remote_type = models.CharField(max_length=10, choices=REMOTE_TYPES, default='onsite')
    is_remote = models.BooleanField(default=False)
    
    # Compensation
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    salary_visible = models.BooleanField(default=True)
    
    # Job Details
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default='full-time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid')
    openings = models.PositiveIntegerField(default=1)
    
    # Dates
    application_deadline = models.DateField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    
    # Status & Stats
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    views_count = models.PositiveIntegerField(default=0)
    applications_count = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['company', '-created_at']),
            models.Index(fields=['category', '-created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        
        if self.status == 'active' and not self.published_at:
            self.published_at = timezone.now()
        
        if self.application_deadline:
            self.expires_at = timezone.make_aware(
                datetime.combine(self.application_deadline, datetime.min.time())
            )
        
        super().save(*args, **kwargs)
    
    def is_active(self):
        """Check if job is still active"""
        if self.status != 'active':
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True
    
    def get_salary_range(self):
        """Get formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f}+"
        return "Not specified"
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"

class JobApplication(models.Model):
    """Job application model"""
    
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('shortlisted', 'Shortlisted'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
        ('withdrawn', 'Withdrawn'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    
    # Application documents
    resume = models.FileField(upload_to='resumes/')
    cover_letter = models.TextField(blank=True)
    portfolio_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    notes = models.TextField(blank=True)  # Employer notes
    
    # Tracking
    viewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['job', 'applicant']
    
    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"

class SavedJob(models.Model):
    """Saved jobs for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'job']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"

class JobAlert(models.Model):
    """Job alerts for users"""
    
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_alerts')
    keyword = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    employment_type = models.CharField(max_length=20, choices=Job.EMPLOYMENT_TYPES, blank=True, null=True)
    remote_type = models.CharField(max_length=10, choices=Job.REMOTE_TYPES, blank=True, null=True)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default='weekly')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Job alert for {self.user.username}"