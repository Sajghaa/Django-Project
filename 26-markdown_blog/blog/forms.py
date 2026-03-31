from django import forms
from .models import Post, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'content', 'excerpt', 'category', 'status', 'featured_image']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 20, 'placeholder': 'Write your post in Markdown...'}),
            'excerpt': forms.Textarea(attrs={'rows': 3, 'placeholder': 'A short summary of your post...'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your comment here...'}),
        }