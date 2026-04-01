from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone

class Department(models.Model):
    """Department model for organizing employees"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Department code (e.g., IT, HR)")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        ordering = ['name']

class Position(models.Model):
    """Job position model"""
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    description = models.TextField(blank=True)
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.title} - {self.department.name}"
    
    class Meta:
        ordering = ['title']

class Employee(models.Model):
    """Employee model with complete information"""
    
    # Employment Status Choices
    EMPLOYMENT_STATUS = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
        ('temporary', 'Temporary'),
    )
    
    # Gender Choices
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    # Marital Status
    MARITAL_STATUS = (
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    )
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be valid")]
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS, default='single')
    
    # Address Information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='USA')
    
    # Employment Information
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True, related_name='employees')
    employment_status = models.CharField(max_length=20, choices=EMPLOYMENT_STATUS, default='full_time')
    hire_date = models.DateField(default=timezone.now)
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Manager/Supervisor
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    # Skills and Qualifications
    skills = models.TextField(blank=True, help_text="List skills separated by commas")
    education = models.TextField(blank=True, help_text="Educational background")
    
    # Documents
    profile_picture = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    
    # System Information
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['email']),
            models.Index(fields=['department']),
        ]
    
    def save(self, *args, **kwargs):
        # Generate employee ID if not exists
        if not self.employee_id:
            import random
            import string
            year = timezone.now().year
            random_digits = ''.join(random.choices(string.digits, k=4))
            self.employee_id = f"EMP{year}{random_digits}"
        super().save(*args, **kwargs)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_absolute_url(self):
        return reverse('employees:employee_detail', kwargs={'pk': self.pk})
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.employee_id})"
    
    @property
    def age(self):
        from datetime import date
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def experience_years(self):
        from datetime import date
        today = date.today()
        return today.year - self.hire_date.year - ((today.month, today.day) < (self.hire_date.month, self.hire_date.day))