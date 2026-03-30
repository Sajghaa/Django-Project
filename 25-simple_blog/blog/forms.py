from django import forms
from django.core.exceptions import ValidationError
from .models import Post, Comment, Newsletter, Category, Tag

class PostForm(forms.ModelForm):
    tags_input = forms.CharField(
        max_length=500,
        required=False,
        help_text="Enter tags separated by commas (e.g., python, django, web)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'python, django, web'})
    )
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'tags_input', 'content', 'excerpt', 
                  'featured_image', 'status', 'featured', 'allow_comments', 
                  'seo_title', 'seo_description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter post title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 15, 'placeholder': 'Write your post content here (supports Markdown)...'}),
            'excerpt': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Short summary of your post (max 300 chars)'}),
            'featured_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seo_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'SEO Title (optional)'}),
            'seo_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'SEO Description (optional)'}),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 50:
            raise ValidationError('Content must be at least 50 characters long.')
        return content
    
    def clean_tags_input(self):
        tags = self.cleaned_data.get('tags_input')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            if len(tag_list) > 10:
                raise ValidationError('Maximum 10 tags allowed.')
            return tags
        return ''

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Your Website (optional)'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your comment...'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise ValidationError('Name must be at least 2 characters long.')
        return name
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 5:
            raise ValidationError('Comment must be at least 5 characters long.')
        return content

class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Newsletter.objects.filter(email=email).exists():
            raise ValidationError('This email is already subscribed!')
        return email

class SearchForm(forms.Form):
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Search posts...'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="All Categories",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    order_by = forms.ChoiceField(
        choices=[
            ('-published_at', 'Newest'),
            ('published_at', 'Oldest'),
            ('-views', 'Most Viewed'),
            ('-likes', 'Most Liked'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )