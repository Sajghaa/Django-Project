from django import forms
from .models import Comment, CommentReport

class CommentForm(forms.ModelForm):
    """Form for creating and editing comments"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'comment-form-content',
                'rows': 4,
                'placeholder': 'Write your comment here...',
                'required': True
            }),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 3:
            raise forms.ValidationError('Comment must be at least 3 characters long.')
        if len(content) > 5000:
            raise forms.ValidationError('Comment cannot exceed 5000 characters.')
        return content

class CommentReplyForm(forms.ModelForm):
    """Form for replying to comments"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'comment-form-content',
                'rows': 3,
                'placeholder': 'Write your reply...',
                'required': True
            }),
        }

class CommentReportForm(forms.ModelForm):
    """Form for reporting inappropriate comments"""
    
    class Meta:
        model = CommentReport
        fields = ['reason', 'details']
        widgets = {
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Please provide additional details (optional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].empty_label = 'Select a reason'

class CommentSearchForm(forms.Form):
    """Form for searching comments"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search comments...'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All')] + list(Comment.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )