from django import forms
from django.core.exceptions import ValidationError
from .models import Service, Booking, Review
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    """Form for creating a booking"""
    
    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    class Meta:
        model = Booking
        fields = ['start_datetime', 'guests_count', 'special_requests']
        widgets = {
            'guests_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'special_requests': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests?'
            }),
        }
    
    def clean_start_datetime(self):
        start_datetime = self.cleaned_data.get('start_datetime')
        
        if start_datetime < datetime.now():
            raise ValidationError('Cannot book in the past')
        
        if start_datetime > datetime.now() + timedelta(days=90):
            raise ValidationError('Cannot book more than 90 days in advance')
        
        return start_datetime

class ReviewForm(forms.ModelForm):
    """Form for leaving a review"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}, choices=[
                (1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')
            ]),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience...'
            }),
        }

class ServiceFilterForm(forms.Form):
    """Form for filtering services"""
    
    service_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Service.SERVICE_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min Price'})
    )
    max_price = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max Price'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search services...'})
    )

class DateAvailabilityForm(forms.Form):
    """Form for checking availability"""
    
    date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    guests = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )