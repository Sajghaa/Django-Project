from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel
import uuid

class Expense(BaseModel):
    """Main expense model"""
    
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash'
        CREDIT_CARD = 'credit_card', 'Credit Card'
        DEBIT_CARD = 'debit_card', 'Debit Card'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        MOBILE_MONEY = 'mobile_money', 'Mobile Money'
        OTHER = 'other', 'Other'
    
    class ExpenseType(models.TextChoices):
        NECESSITY = 'necessity', 'Necessity'
        WANT = 'want', 'Want'
        SAVINGS = 'savings', 'Savings'
        INVESTMENT = 'investment', 'Investment'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expenses')
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True, related_name='expenses')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    date = models.DateField()
    
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    expense_type = models.CharField(max_length=20, choices=ExpenseType.choices, default=ExpenseType.NECESSITY)
    
    receipt = models.FileField(upload_to='receipts/%Y/%m/%d/', null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurring_period = models.IntegerField(null=True, blank=True, help_text="Days between recurring expenses")
    
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        return f"{self.title} - ${self.amount} on {self.date}"
    
    @property
    def formatted_amount(self):
        return f"${self.amount:,.2f}"
    
    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]

class RecurringExpense(BaseModel):
    """Recurring expense configuration"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recurring_expenses')
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='recurring_config')
    
    frequency_days = models.IntegerField(validators=[MinValueValidator(1)])
    next_due_date = models.DateField()
    last_generated = models.DateField(null=True, blank=True)
    auto_generate = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Recurring: {self.expense.title} every {self.frequency_days} days"