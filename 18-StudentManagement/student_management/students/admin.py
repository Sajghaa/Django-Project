from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_id', 'email', 'gpa', 'created_at')
    search_fields = ('name', 'student_id', 'email')
    list_filter = ('created_at',)