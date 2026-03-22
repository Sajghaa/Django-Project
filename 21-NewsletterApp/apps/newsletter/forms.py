from django import forms
from django.core.exceptions import ValidationError
from .models import Subscriber, Newsletter

class SubscribeForm(forms.ModelForm):
    """Form for newsletter subscription"""
    confirm_email = forms.EmailField(label='Confirm Email')
    
    class Meta:
        model = Subscriber
        fields = ['email', 'first_name', 'last_name', 'receive_promotions']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name (optional)'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name (optional)'}),
            'receive_promotions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        
        if email and confirm_email and email != confirm_email:
            raise ValidationError('Email addresses do not match.')
        
        if email and Subscriber.objects.filter(email=email, status='active').exists():
            raise ValidationError('This email is already subscribed to our newsletter.')
        
        return cleaned_data

class UnsubscribeForm(forms.Form):
    """Form for unsubscribing"""
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not Subscriber.objects.filter(email=email).exists():
            raise ValidationError('This email is not in our subscriber list.')
        return email

class NewsletterForm(forms.ModelForm):
    """Form for creating/editing newsletters"""
    class Meta:
        model = Newsletter
        fields = ['subject', 'content', 'html_content', 'scheduled_for', 'track_opens', 'track_clicks']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'html_content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'scheduled_for': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'track_opens': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'track_clicks': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }