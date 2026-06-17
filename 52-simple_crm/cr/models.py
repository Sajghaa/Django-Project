from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Customer(models.Model):
    STATUS_CHOICES = (
        ('lead', 'Lead'),
        ('customer', 'Customer'),
        ('partner', 'Partner'),
        ('inactive', 'Inactive'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='USA')
    industry = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='lead')
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contact_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.full_name

class Interaction(models.Model):
    TYPE_CHOICES = (
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('note', 'Note'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    subject = models.CharField(max_length=200)
    description = models.TextField()
    date_time = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_time']
    
    def __str__(self):
        return f"{self.get_type_display()} with {self.customer.full_name}"

class Lead(models.Model):
    SOURCE_CHOICES = (
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('email', 'Email'),
        ('call', 'Call'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('lost', 'Lost'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leads')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True)
    converted_to_customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='converted_from_lead')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __str__(self):
        return self.full_name

class Opportunity(models.Model):
    STAGE_CHOICES = (
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='opportunities')
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting')
    probability = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=10,
        help_text="Probability percentage"
    )
    expected_close = models.DateField(null=True, blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='opportunities')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name