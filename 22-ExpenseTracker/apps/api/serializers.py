from rest_framework import serializers
from ..expenses.models import Expense
from ..categories.models import Category
from ..budgets.models import Budget

class ExpenseSerializer(serializers.ModelSerializer):
    formatted_amount = serializers.ReadOnlyField()
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Expense
        fields = ['id', 'title', 'description', 'amount', 'formatted_amount', 'date', 
                 'category', 'category_name', 'payment_method', 'receipt', 'tags', 
                 'created_at', 'updated_at']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'color', 'created_at']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id', 'category', 'amount', 'period', 'month', 'year', 'created_at']