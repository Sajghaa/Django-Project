from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import URL
from .utils import validate_url

class URLShortenForm(forms.ModelForm):
    """Form for creating short URLs"""
    
    custom_alias = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Custom alias (optional)'
        }),
        help_text="Leave blank for auto-generated code"
    )
    
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password protection (optional)'
        })
    )
    
    class Meta:
        model = URL
        fields = ['original_url', 'title', 'description', 'expires_at']
        widgets = {
            'original_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/very/long/url',
                'required': True
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Title (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Description (optional)'
            }),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def clean_original_url(self):
        url = self.cleaned_data.get('original_url')
        if not validate_url(url):
            raise forms.ValidationError('Please enter a valid URL (include http:// or https://)')
        return url
    
    def clean_custom_alias(self):
        alias = self.cleaned_data.get('custom_alias')
        if alias:
            if not alias.isalnum():
                raise forms.ValidationError('Custom alias can only contain letters and numbers')
            if URL.objects.filter(custom_alias=alias).exists():
                raise forms.ValidationError('This alias is already taken')
        return alias

class URLSearchForm(forms.Form):
    """Form for searching URLs"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by original URL or short code...'
        })
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-total_clicks', 'Most Clicks'),
            ('-total_clicks', 'Least Clicks'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class PasswordForm(forms.Form):
    """Form for password-protected URLs"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

class RegistrationForm(UserCreationForm):
    """User registration form"""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email address'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    """User login form"""
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))