from django.db import models
from django.core.validators import MinLengthValidator
class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField (
        max_length=10, 
        validators=[MinLengthValidator(5)],
        unique=True
        )
    email = models.EmailField()
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name