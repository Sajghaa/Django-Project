from django.db import models
from django.core.exceptions import ValidationError

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = memoryview.CharFields(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)

    category = models.CharField(max_length=100, blank=True)
    published_date = models.DateField(null=True, blank=True)

    total_copies = models.PositiveIntegerField(default = 1)
    available_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):

        if self.available_copies > self.total_copies:
            raise ValidationError(
                "Available copies cannot exceed total copies"
            )
    
    def __str__(self):
        return f"{self.title} by {self.author}"
