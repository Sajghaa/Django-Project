from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import uuid

class Class(models.Model):
    """School classes/sections"""
    name = models.CharField(max_length=50)  # Class 1, Class 2, etc.
    section = models.CharField(max_length=10, blank=True)  # A, B, C
    class_teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='class_teacher')
    room_number = models.CharField(max_length=20, blank=True)
    capacity = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = 'Classes'
        unique_together = ['name', 'section']
        ordering = ['name', 'section']
    
    def __str__(self):
        return f"{self.name} - {self.section}" if self.section else self.name

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('transferred', 'Transferred'),
        ('expelled', 'Expelled'),
    )
    
    admission_number = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    class_assigned = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='students')
    roll_number = models.PositiveIntegerField(null=True, blank=True)
    joining_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['class_assigned', 'roll_number', 'first_name']
        unique_together = ['class_assigned', 'roll_number']
    
    def save(self, *args, **kwargs):
        if not self.admission_number:
            year = timezone.now().year
            last_student = Student.objects.order_by('-id').first()
            next_id = (last_student.id + 1) if last_student else 1
            self.admission_number = f"{year}{next_id:06d}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.admission_number} - {self.full_name}"

class Parent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parents')
    father_name = models.CharField(max_length=100, blank=True)
    father_phone = models.CharField(max_length=20, blank=True)
    father_email = models.EmailField(blank=True)
    mother_name = models.CharField(max_length=100, blank=True)
    mother_phone = models.CharField(max_length=20, blank=True)
    mother_email = models.EmailField(blank=True)
    guardian_name = models.CharField(max_length=100, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    
    def __str__(self):
        return f"Parents of {self.student.full_name}"

class Teacher(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('on_leave', 'On Leave'),
        ('resigned', 'Resigned'),
    )
    
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    qualification = models.CharField(max_length=200, blank=True)
    specialization = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(default=timezone.now)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    address = models.TextField()
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['first_name', 'last_name']
    
    def save(self, *args, **kwargs):
        if not self.employee_id:
            year = timezone.now().year
            last_teacher = Teacher.objects.order_by('-id').first()
            next_id = (last_teacher.id + 1) if last_teacher else 1
            self.employee_id = f"TCH{year}{next_id:04d}"
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return f"{self.employee_id} - {self.full_name}"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='subjects')
    theory_marks = models.IntegerField(default=100)
    practical_marks = models.IntegerField(default=0)
    is_elective = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        unique_together = ['class_assigned', 'code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Timetable(models.Model):
    DAY_CHOICES = (
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    )
    
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetable')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetable')
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=20, blank=True)
    
    class Meta:
        ordering = ['day_of_week', 'start_time']
        unique_together = ['class_assigned', 'day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.class_assigned} - {self.subject.name} on {self.get_day_of_week_display()} at {self.start_time}"

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True)
    marked_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='attendance_marked')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"

class Exam(models.Model):
    TERM_CHOICES = (
        ('quarterly', 'Quarterly'),
        ('half_yearly', 'Half Yearly'),
        ('annual', 'Annual'),
    )
    
    name = models.CharField(max_length=100)
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='exams')
    term = models.CharField(max_length=20, choices=TERM_CHOICES)
    exam_date = models.DateField()
    year = models.IntegerField(default=timezone.now().year)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-exam_date']
        unique_together = ['class_assigned', 'term', 'year']
    
    def __str__(self):
        return f"{self.class_assigned} - {self.name} ({self.year})"

class Grade(models.Model):
    GRADE_CHOICES = (
        ('A+', 'A+'),
        ('A', 'A'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='grades')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades')
    theory_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    practical_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'exam']
        ordering = ['exam', 'subject']
    
    def save(self, *args, **kwargs):
        self.total_marks = self.theory_marks + self.practical_marks
        max_marks = self.subject.theory_marks + self.subject.practical_marks
        if max_marks > 0:
            self.percentage = (self.total_marks / max_marks) * 100
        else:
            self.percentage = 0
        
        # Determine grade based on percentage
        if self.percentage >= 90:
            self.grade = 'A+'
        elif self.percentage >= 80:
            self.grade = 'A'
        elif self.percentage >= 70:
            self.grade = 'B+'
        elif self.percentage >= 60:
            self.grade = 'B'
        elif self.percentage >= 50:
            self.grade = 'C+'
        elif self.percentage >= 40:
            self.grade = 'C'
        elif self.percentage >= 33:
            self.grade = 'D'
        else:
            self.grade = 'F'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name} - {self.grade}"

class FeeStructure(models.Model):
    FEE_TYPE_CHOICES = (
        ('tuition', 'Tuition Fee'),
        ('admission', 'Admission Fee'),
        ('exam', 'Exam Fee'),
        ('library', 'Library Fee'),
        ('sports', 'Sports Fee'),
        ('transport', 'Transport Fee'),
        ('other', 'Other'),
    )
    
    class_assigned = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='fee_structures')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['class_assigned', 'fee_type']
        ordering = ['fee_type']
    
    def __str__(self):
        return f"{self.class_assigned} - {self.get_fee_type_display()}: ${self.amount}"

class FeePayment(models.Model):
    STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('partial', 'Partial'),
    )
    
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('bank', 'Bank Transfer'),
        ('online', 'Online Payment'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_payments')
    fee_type = models.CharField(max_length=20, choices=FeeStructure.FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.receipt_number:
            self.receipt_number = f"RCP{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.receipt_number} - {self.student.full_name} - ${self.amount}"