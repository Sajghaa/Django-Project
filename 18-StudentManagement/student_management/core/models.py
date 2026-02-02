from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
from django.utils import timezone
from datetime import date

class Department(models.Model):
    """Academic department"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def student_count(self):
        return self.students.count()

class Student(models.Model):
    """Student model"""
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graated'),
        ('suspended', 'Suspended'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    student_id = models.CharField(max_length=20, unique=True, blank=True)  # Will auto-generate
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    
    # Contact Information
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    # Academic Information
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name='students'
    )
    enrollment_date = models.DateField(default=date.today)
    graduation_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Additional
    profile_picture = models.ImageField(
        upload_to='student_profiles/',
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-enrollment_date', 'last_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.student_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def save(self, *args, **kwargs):
        """Auto-generate student ID if not provided"""
        if not self.student_id:
            year = self.enrollment_date.year
            dept_code = self.department.code
            last_student = Student.objects.filter(
                department=self.department,
                enrollment_date__year=year
            ).order_by('-id').first()
            
            if last_student and last_student.student_id:
                try:
                    last_roll = int(last_student.student_id.split('-')[-1])
                    new_roll = last_roll + 1
                except:
                    new_roll = 1
            else:
                new_roll = 1
            
            self.student_id = f"{dept_code}-{year}-{new_roll:03d}"
        
        super().save(*args, **kwargs)

class Course(models.Model):
    """Course model"""
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    credit_hours = models.IntegerField(default=3)
    description = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['department', 'code']
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(models.Model):
    """Student enrollment in courses"""
    GRADE_CHOICES = [
        ('A', 'A'), ('B', 'B'), ('C', 'C'),
        ('D', 'D'), ('F', 'F'), ('', 'Not Graded'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    enrollment_date = models.DateField(auto_now_add=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, default='')
    
    class Meta:
        unique_together = ['student', 'course', 'semester']
        ordering = ['-enrollment_date']
    
    def __str__(self):
        return f"{self.student} - {self.course} (Sem {self.semester})"
    
    @property
    def is_passed(self):
        return self.grade in ['A', 'B', 'C', 'D'] and self.grade != ''

class Result(models.Model):
    """Student semester result"""
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='results'
    )
    semester = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)]
    )
    total_credits = models.IntegerField(default=0)
    earned_credits = models.IntegerField(default=0)
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )
    
    class Meta:
        unique_together = ['student', 'semester']
        ordering = ['student', 'semester']
    
    def __str__(self):
        return f"{self.student} - Sem {self.semester}: GPA {self.gpa}"