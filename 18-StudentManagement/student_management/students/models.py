from django.db import models
from django.core.validators import MinLengthValidator
class Student(models.Model):
    name = models.CharField(max_length=100)
    student_id = models.CharField (
        max_length=10, 
        validators=[MinLengthValidator(5)]
        )

    def __str__(self):
        return self.name