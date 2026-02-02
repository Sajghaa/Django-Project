from django import forms
from django.core.exceptions import ValidationError
from .models import Student, Department, Course, Enrollment

class StudentForm(forms.ModelForm):
    """Form for creating/updating students"""
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Format: YYYY-MM-DD"
    )
    enrollment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    graduation_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'blood_group', 'email', 'phone', 'address', 'emergency_contact',
            'department', 'enrollment_date', 'graduation_date', 'status',
            'profile_picture'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'gender': forms.RadioSelect(),
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if Student.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A student with this email already exists.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        enrollment_date = cleaned_data.get('enrollment_date')
        graduation_date = cleaned_data.get('graduation_date')
        
        if graduation_date and enrollment_date and graduation_date < enrollment_date:
            raise ValidationError("Graduation date cannot be before enrollment date.")
        
        return cleaned_data

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name', 'code', 'description']

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['department', 'code', 'name', 'credit_hours', 'description']

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'semester', 'grade']
        widgets = {
            'semester': forms.NumberInput(attrs={'min': 1, 'max': 8}),
        }