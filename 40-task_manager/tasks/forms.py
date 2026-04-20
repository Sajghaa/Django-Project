from django import forms
from django.utils import timezone
from .models import Task, Category, Project, Subtask, Reminder

class TaskForm(forms.ModelForm):
    """Form for creating and editing tasks"""
    
    due_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'category', 'project', 'priority', 
                  'due_date', 'estimated_hours', 'tags', 'attachment']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Task description...'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'project': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'estimated_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Estimated hours'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'work, urgent, meeting'
            }),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            raise forms.ValidationError('Due date cannot be in the past.')
        return due_date
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['project'].queryset = Project.objects.filter(user=user)

class SubtaskForm(forms.ModelForm):
    """Form for adding subtasks"""
    
    class Meta:
        model = Subtask
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subtask title'
            }),
        }

class CategoryForm(forms.ModelForm):
    """Form for categories"""
    
    class Meta:
        model = Category
        fields = ['name', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category name'}),
            'color': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('primary', 'Blue'),
                ('success', 'Green'),
                ('danger', 'Red'),
                ('warning', 'Yellow'),
                ('info', 'Cyan'),
                ('dark', 'Dark'),
            ]),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-tag'}),
        }

class ProjectForm(forms.ModelForm):
    """Form for projects"""
    
    class Meta:
        model = Project
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Project description'}),
            'color': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('primary', 'Blue'),
                ('success', 'Green'),
                ('danger', 'Red'),
                ('warning', 'Yellow'),
                ('info', 'Cyan'),
                ('dark', 'Dark'),
            ]),
        }

class TaskFilterForm(forms.Form):
    """Form for filtering tasks"""
    
    STATUS_CHOICES = [('', 'All Status')] + list(Task.STATUS_CHOICES)
    PRIORITY_CHOICES = [('', 'All Priority')] + list(Task.PRIORITY_CHOICES)
    
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, 
                               widget=forms.Select(attrs={'class': 'form-control'}))
    priority = forms.ChoiceField(choices=PRIORITY_CHOICES, required=False,
                                  widget=forms.Select(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False,
                                       widget=forms.Select(attrs={'class': 'form-control'}))
    project = forms.ModelChoiceField(queryset=Project.objects.none(), required=False,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search tasks...'
    }))
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['project'].queryset = Project.objects.filter(user=user)