from django import forms
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import File
import os

class FileUploadForm(forms.ModelForm):
    """Form for uploading files"""
    
    class Meta:
        model = File
        fields = ['file', 'title', 'description', 'access_type', 'expires_at', 'max_downloads', 'password']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'File title (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'File description (optional)'}),
            'access_type': forms.Select(attrs={'class': 'form-control'}),
            'expires_at': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'max_downloads': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'value': 0}),
            'password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password (optional)'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        # Check file size
        if file.size > settings.MAX_UPLOAD_SIZE:
            raise ValidationError(f'File too large. Max size is {settings.MAX_UPLOAD_SIZE // 1048576}MB')
        
        # Check file type
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in settings.ALLOWED_FILE_TYPES:
            raise ValidationError(f'File type not allowed. Allowed types: {", ".join(settings.ALLOWED_FILE_TYPES)}')
        
        return file
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 4:
            raise ValidationError('Password must be at least 4 characters')
        return password

class ShareFileForm(forms.Form):
    """Form for sharing files with users"""
    usernames = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter usernames separated by commas'}),
        help_text='Enter usernames separated by commas'
    )
    
    def clean_usernames(self):
        usernames = self.cleaned_data.get('usernames')
        username_list = [u.strip() for u in usernames.split(',') if u.strip()]
        return username_list

class FilePasswordForm(forms.Form):
    """Form for password-protected files"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter file password'}),
        label='Password'
    )

class FileSearchForm(forms.Form):
    """Form for searching files"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search files...'})
    )
    file_type = forms.ChoiceField(
        choices=[('', 'All Types')] + [
            ('PDF Document', 'PDF'),
            ('Word Document', 'Word'),
            ('Text File', 'Text'),
            ('JPEG Image', 'Image'),
            ('PNG Image', 'Image'),
            ('ZIP Archive', 'Archive'),
            ('Excel Spreadsheet', 'Excel'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('-file_size', 'Largest First'),
            ('file_size', 'Smallest First'),
            ('-download_count', 'Most Downloaded'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )