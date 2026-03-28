from django import forms
from .models import Movie, Rating

class MovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'genre', 'release_year', 'director', 'description', 'duration', 'poster', 'poster_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter movie title'}),
            'genre': forms.Select(attrs={'class': 'form-control'}),
            'release_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'YYYY'}),
            'director': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Director name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Movie description'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Duration in minutes'}),
            'poster': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'poster_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://example.com/poster.jpg'}),
        }
    
    def clean_release_year(self):
        year = self.cleaned_data.get('release_year')
        if year and year > 2025:
            raise forms.ValidationError("Release year cannot be in the future!")
        return year
    
    def clean_duration(self):
        duration = self.cleaned_data.get('duration')
        if duration and duration < 1:
            raise forms.ValidationError("Duration must be at least 1 minute!")
        return duration

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review here...'}),
        }