from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.core.models import BaseModel
import uuid

class Budget(BaseModel):
    """Budget model"""
    
    class Period(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'
        QUARTERLY = 'quarterly', 'Quarterly'
        YEARLY = 'yearly', 'Yearly'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey('categories.Category', on_delete=models.CASCADE, related_name='budgets')
    
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    period = models.CharField(max_length=20, choices=Period.choices, default=Period.MONTHLY)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    alert_threshold = models.IntegerField(default=80, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.category.name} - ${self.amount} ({self.period})"
    
    def get_spent_amount(self):
        """Calculate amount spent against this budget"""
        from apps.expenses.models import Expense
        expenses = Expense.objects.filter(
            user=self.user,
            category=self.category,
            date__gte=self.start_date
        )
        if self.end_date:
            expenses = expenses.filter(date__lte=self.end_date)
        return expenses.aggregate(total=models.Sum('amount'))['total'] or 0
    
    def get_remaining_amount(self):
        """Calculate remaining budget amount"""
        return self.amount - self.get_spent_amount()
    
    def get_percentage_used(self):
        """Calculate percentage of budget used"""
        if self.amount > 0:
            return (self.get_spent_amount() / self.amount) * 100
        return 0