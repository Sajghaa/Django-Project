from django import forms
from django.utils import timezone
from .models import Budget
from ..categories.models import Category

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'period', 'start_date', 'end_date', 'alert_threshold']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'alert_threshold': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'instance') and self.instance.pk:
            user = self.instance.user
        elif 'initial' in kwargs and 'user' in kwargs['initial']:
            user = kwargs['initial']['user']
        else:
            user = None
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        
        # Set default start date to first day of current month
        if not self.instance.pk:
            today = timezone.now().date()
            self.fields['start_date'].initial = today.replace(day=1)
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date")
        
        return cleaned_data