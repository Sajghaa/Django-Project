from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    description = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.file.name