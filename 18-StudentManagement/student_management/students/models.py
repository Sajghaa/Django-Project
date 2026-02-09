from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=10, unique=True)
    email = models.EmailField()
    gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(4.0)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_academic_status(self):
        if self.gpa >= 3.5:
            return "Excellent"
        elif self.gpa >= 2.0:
            return "Good"
        else:
            return "Needs Improvement"
    
    @property
    def name_with_id(self):
        return f"{self.name} ({self.student_id})"