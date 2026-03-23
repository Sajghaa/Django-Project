from django.db import models
from django.conf import settings
from apps.core.models import BaseModel
import uuid

class Category(BaseModel):
    """Expense category model"""
    
    class CategoryType(models.TextChoices):
        INCOME = 'income', 'Income'
        EXPENSE = 'expense', 'Expense'
        BOTH = 'both', 'Both'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='categories')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-tag')
    color = models.CharField(max_length=7, default='#6c757d')
    category_type = models.CharField(max_length=10, choices=CategoryType.choices, default=CategoryType.EXPENSE)
    
    budget_limit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_period = models.CharField(max_length=20, default='monthly')
    
    class Meta:
        ordering = ['name']
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', 'category_type']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_total_expenses(self, start_date=None, end_date=None):
        """Get total expenses for this category"""
        expenses = self.expenses.filter(user=self.user)
        if start_date:
            expenses = expenses.filter(date__gte=start_date)
        if end_date:
            expenses = expenses.filter(date__lte=end_date)
        return expenses.aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def budget_used_percentage(self):
        """Calculate percentage of budget used"""
        if self.budget_limit:
            total = self.get_total_expenses()
            return (total / self.budget_limit) * 100
        return 0