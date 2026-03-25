from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Custom user model with additional fields"""
    
    class Currency(models.TextChoices):
        USD = 'USD', 'US Dollar'
        EUR = 'EUR', 'Euro'
        GBP = 'GBP', 'British Pound'
        JPY = 'JPY', 'Japanese Yen'
        CAD = 'CAD', 'Canadian Dollar'
        AUD = 'AUD', 'Australian Dollar'
        CNY = 'CNY', 'Chinese Yuan'
        INR = 'INR', 'Indian Rupee'
    
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default='USD')
    
    # Preferences
    #default_category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_for_users')
    email_notifications = models.BooleanField(default=True)
    budget_alerts = models.BooleanField(default=True)
    
    # Statistics
    total_expenses = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_income = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def update_totals(self):
        """Update user's total expenses and income"""
        from apps.expenses.models import Expense
        
        self.total_expenses = Expense.objects.filter(
            user=self, 
            expense_type='necessity'
        ).aggregate(total=models.Sum('amount'))['total'] or 0
        
        self.save()