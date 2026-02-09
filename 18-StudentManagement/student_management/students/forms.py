from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'student_id', 'email', 'gpa']
        widgets = {
            'gpa': forms.NumberInput(attrs={'step': '0.01', 'min': '0.0', 'max': '4.0'}),
        }
        help_texts = {
            'gpa': 'Enter GPA between 0.0 and 4.0',
        }