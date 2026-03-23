import uuid
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    """Abstract base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def soft_delete(self):
        """Soft delete the record"""
        self.is_active = False
        self.save()
    
    def restore(self):
        """Restore soft deleted record"""
        self.is_active = True
        self.save()

class TimeStampedModel(models.Model):
    """Model with timestamp fields only"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']

class UUIDModel(models.Model):
    """Model with UUID primary key"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    class Meta:
        abstract = True