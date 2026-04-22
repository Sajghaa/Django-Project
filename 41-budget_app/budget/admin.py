from django.contrib import admin
from .models import Category, Transaction, Budget, SavingsGoal

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'type', 'is_default', 'created_at']
    list_filter = ['type', 'is_default']
    search_fields = ['name', 'user__username']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'amount', 'transaction_date', 'payment_method', 'created_at']
    list_filter = ['category__type', 'payment_method', 'transaction_date']
    search_fields = ['user__username', 'description']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['user', 'category', 'month', 'year', 'amount', 'spent_amount']
    list_filter = ['month', 'year']
    search_fields = ['user__username']

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'target_amount', 'current_amount', 'target_date', 'is_completed']
    list_filter = ['is_completed', 'priority']
    search_fields = ['user__username', 'name']