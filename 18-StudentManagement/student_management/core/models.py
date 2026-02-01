# core/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, EmailValidator
import uuid
from datetime import date

class BaseModel(models.Model):
    """Abstract base model for common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class Department(BaseModel):
    """Academic department"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def student_count(self):
        return self.students.count()

class Student(BaseModel):
    """Student model with all necessary fields"""
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
    
    # Personal Information
    student_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Format: DEPT-YEAR-ROLL (e.g., CS-2023-001)"
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    
    # Contact Information
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    # Academic Information
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,  # Prevent deletion if students exist
        related_name='students'
    )
    enrollment_date = models.DateField(default=date.today)
    graduation_date = models.DateField(null=True, blank=True)
    
    # Status
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('graduated', 'Graated'),
        ('suspended', 'Suspended'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Additional
    profile_picture = models.ImageField(
        upload_to='student_profiles/',
        blank=True,
        null=True
    )
    
    class Meta:
        ordering = ['-enrollment_date', 'student_id']
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['email']),
            models.Index(fields=['status']),
        ]
    
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
    
    @property
    def is_graduated(self):
        return self.status == 'graduated'
    
    @property
    def current_semester(self):
        """Calculate current semester based on enrollment date"""
        from dateutil.relativedelta import relativedelta
        if self.is_graduated:
            return "Graated"
        
        today = date.today()
        months_enrolled = (today.year - self.enrollment_date.year) * 12 + today.month - self.enrollment_date.month
        semester = (months_enrolled // 6) + 1
        return f"Semester {semester}"
    
    def save(self, *args, **kwargs):
        """Auto-generate student ID if not provided"""
        if not self.student_id:
            # Generate ID: DEPTCODE-YEAR-ROLLNUM
            year = self.enrollment_date.year
            dept_code = self.department.code
            last_student = Student.objects.filter(
                department=self.department,
                enrollment_date__year=year
            ).order_by('student_id').last()
            
            if last_student:
                last_roll = int(last_student.student_id.split('-')[-1])
                new_roll = last_roll + 1
            else:
                new_roll = 1
            
            self.student_id = f"{dept_code}-{year}-{new_roll:03d}"
        
        super().save(*args, **kwargs)

class Course(BaseModel):
    """Course model"""
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    credit_hours = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['code']
        unique_together = ['department', 'name']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Enrollment(BaseModel):
    """Student enrollment in courses"""
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
    grade = models.CharField(
        max_length=2,
        blank=True,
        choices=[
            ('A', 'A'), ('B', 'B'), ('C', 'C'),
            ('D', 'D'), ('F', 'F'), ('I', 'Incomplete'),
        ]
    )
    
    class Meta:
        ordering = ['-enrollment_date']
        unique_together = ['student', 'course', 'semester']
    
    def __str__(self):
        return f"{self.student} - {self.course} (Sem {self.semester})"
    
    @property
    def is_passed(self):
        return self.grade in ['A', 'B', 'C', 'D']
    
    @property
    def grade_point(self):
        grade_points = {'A': 4.0, 'B': 3.0, 'C': 2.0, 'D': 1.0, 'F': 0.0}
        return grade_points.get(self.grade, 0.0)

class Result(BaseModel):
    """Student result/semester GPA"""
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
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )
    
    class Meta:
        ordering = ['student', 'semester']
        unique_together = ['student', 'semester']
    
    def __str__(self):
        return f"{self.student} - Sem {self.semester}: GPA {self.gpa}"
    
    def calculate_gpa(self):
        """Calculate GPA from enrollments"""
        enrollments = Enrollment.objects.filter(
            student=self.student,
            semester=self.semester
        )
        
        total_points = 0
        total_credits = 0
        earned_credits = 0
        
        for enrollment in enrollments:
            if enrollment.grade:  # Only if graded
                total_points += enrollment.grade_point * enrollment.course.credit_hours
                total_credits += enrollment.course.credit_hours
                if enrollment.is_passed:
                    earned_credits += enrollment.course.credit_hours
        
        self.total_credits = total_credits
        self.earned_credits = earned_credits
        self.gpa = (total_points / total_credits) if total_credits > 0 else 0.0
        self.save()