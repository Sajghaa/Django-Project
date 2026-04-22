from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Category(models.Model):
    """Transaction category (Income or Expense)"""
    
    TYPE_CHOICES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=50, default='fas fa-tag')
    color = models.CharField(max_length=20, default='primary')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'name', 'type']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Transaction(models.Model):
    """Financial transaction (Income or Expense)"""
    
    PAYMENT_METHODS = (
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Payment'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    description = models.TextField(max_length=500, blank=True)
    transaction_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='cash')
    receipt = models.ImageField(upload_to='receipts/', blank=True, null=True)
    location = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transaction_date', '-created_at']
        indexes = [
            models.Index(fields=['user', '-transaction_date']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.get_type_display()}: {self.amount} - {self.category.name}"
    
    @property
    def get_type_display(self):
        return self.category.type

class Budget(models.Model):
    """Monthly budget for expense categories"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], null=True, blank=True, default=0)  # Allow null
    spent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    alert_threshold = models.IntegerField(default=80, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'category', 'month', 'year']
        ordering = ['category__name']
    
    def __str__(self):
        return f"{self.category.name} - {self.month}/{self.year}: ${self.amount if self.amount else 0}"
    
    @property
    def remaining(self):
        if self.amount:
            return self.amount - self.spent_amount
        return 0
    
    @property
    def percentage_used(self):
        if self.amount and self.amount > 0:
            return min(100, int((self.spent_amount / self.amount) * 100))
        return 0
    
    @property
    def is_exceeded(self):
        return self.amount and self.spent_amount > self.amount
    
    def update_spent(self):
        """Update spent amount based on transactions"""
        from django.db.models import Sum
        total = Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_date__year=self.year,
            transaction_date__month=self.month,
            category__type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0
        self.spent_amount = total
        self.save()

class SavingsGoal(models.Model):
    """Savings goals tracking"""
    
    PRIORITY_CHOICES = (
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Very High'),
        (5, 'Critical'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_goals')
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField()
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['priority', 'target_date']
    
    def __str__(self):
        return f"{self.name} - ${self.current_amount}/${self.target_amount}"
    
    @property
    def remaining_amount(self):
        return self.target_amount - self.current_amount
    
    @property
    def percentage_complete(self):
        if self.target_amount > 0:
            return min(100, int((self.current_amount / self.target_amount) * 100))
        return 0
    
    @property
    def is_overdue(self):
        return not self.is_completed and timezone.now().date() > self.target_date