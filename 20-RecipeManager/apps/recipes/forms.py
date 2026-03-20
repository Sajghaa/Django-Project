from django import forms
from .models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients', 'instructions', 
                  'prep_time', 'cook_time', 'servings', 'difficulty', 'image', 'tags']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'ingredients': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Enter each ingredient on a new line'}),
            'instructions': forms.Textarea(attrs={'rows': 8, 'placeholder': 'Enter step by step instructions'}),
        }