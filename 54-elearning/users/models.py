# apps/users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_instructor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    
    def __str__(self):
        return self.email