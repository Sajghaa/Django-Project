from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
import random
import string

class Service(models.Model):
    """Service model (Hotel Room, Appointment Type, etc.)"""
    
    SERVICE_TYPES = (
        ('hotel', 'Hotel Room'),
        ('appointment', 'Appointment'),
        ('restaurant', 'Restaurant Table'),
        ('spa', 'Spa Service'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES, default='hotel')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField(help_text="Duration in minutes (for appointments)", default=60)
    capacity = models.IntegerField(default=1, help_text="Maximum guests per booking")
    location = models.CharField(max_length=500, blank=True)
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class ServiceAvailability(models.Model):
    """Service availability rules"""
    
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['service', 'day_of_week']
        ordering = ['day_of_week', 'start_time']
    
    def __str__(self):
        return f"{self.service.name} - {self.get_day_of_week_display()}: {self.start_time} to {self.end_time}"

class BlockedDate(models.Model):
    """Blocked dates for maintenance or holidays"""
    
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='blocked_dates')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.service.name} blocked: {self.start_date} to {self.end_date}"

class Booking(models.Model):
    """Booking model"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    )
    
    booking_number = models.CharField(max_length=20, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    
    # Booking details
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    guests_count = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    special_requests = models.TextField(blank=True)
    
    # Pricing
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['booking_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['service', 'start_datetime']),
        ]
    
    def generate_booking_number(self):
        """Generate unique booking number"""
        prefix = 'BK'
        date_str = timezone.now().strftime('%Y%m%d')
        random_digits = ''.join(random.choices(string.digits, k=6))
        return f"{prefix}{date_str}{random_digits}"
    
    def save(self, *args, **kwargs):
        if not self.booking_number:
            self.booking_number = self.generate_booking_number()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.booking_number} - {self.user.username} - {self.service.name}"

class Payment(models.Model):
    """Payment model"""
    
    PAYMENT_METHODS = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, default='pending')
    gateway_response = models.TextField(blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def generate_transaction_id(self):
        """Generate unique transaction ID"""
        return f"TXN{int(timezone.now().timestamp())}{random.randint(1000, 9999)}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.booking.booking_number}"

class Review(models.Model):
    """Review model for services"""
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='review')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.booking.service.name} - {self.rating} stars"