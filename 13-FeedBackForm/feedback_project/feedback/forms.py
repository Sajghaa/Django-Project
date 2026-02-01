from django import forms

class FeedbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        min_length=3,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Your Name'})
    )

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Your Email'})
    )

    message = forms.CharField(
        min_length=10,
        required=True,
        widget=forms.Textarea(attrs={'placeholder': 'Your Feedback'})
    )
