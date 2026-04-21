from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Post, Comment, Category, Tag

class RegistrationForm(UserCreationForm):
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
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        max_length=500,
        required=False,
        help_text="Enter tags separated by commas",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'python, django, web'
        })
    )
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'content', 'excerpt', 'featured_image', 'status', 'seo_title', 'seo_description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Post title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'placeholder': 'Write your post content here...'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short summary for preview'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SEO Title (optional)'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'SEO Description (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].empty_label = "Select Category"

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your comment...'
            }),
        }

class SearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search posts...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sort_by = forms.ChoiceField(
        choices=[
            ('-published_at', 'Newest First'),
            ('published_at', 'Oldest First'),
            ('-views', 'Most Viewed'),
            ('-likes', 'Most Liked'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )