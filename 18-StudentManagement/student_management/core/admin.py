# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Department, Student, Course, Enrollment, Result

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'student_count')
    search_fields = ('name', 'code')
    list_filter = ('is_active',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'department', 'status', 'age')
    list_filter = ('department', 'status', 'gender', 'enrollment_date')
    search_fields = ('student_id', 'first_name', 'last_name', 'email')
    readonly_fields = ('student_id', 'age', 'current_semester')
    fieldsets = (
        ('Personal Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'date_of_birth', 
                      'gender', 'blood_group', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'emergency_contact')
        }),
        ('Academic Information', {
            'fields': ('department', 'enrollment_date', 'graduation_date', 'status')
        }),
        ('Metadata', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('department')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credit_hours')
    list_filter = ('department', 'credit_hours')
    search_fields = ('code', 'name', 'department__name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'grade', 'is_passed')
    list_filter = ('semester', 'grade', 'course__department')
    search_fields = ('student__student_id', 'student__full_name', 'course__code')
    autocomplete_fields = ['student', 'course']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'gpa', 'total_credits', 'earned_credits')
    list_filter = ('semester',)
    search_fields = ('student__student_id', 'student__full_name')
    readonly_fields = ('gpa', 'total_credits', 'earned_credits')