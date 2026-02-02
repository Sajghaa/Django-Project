from django.contrib import admin
from .models import Department, Student, Course, Enrollment, Result

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'student_count')
    search_fields = ('name', 'code')
    list_filter = ('created_at',)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'full_name', 'department', 'status', 'email', 'age')
    list_filter = ('department', 'status', 'gender', 'enrollment_date')
    search_fields = ('student_id', 'first_name', 'last_name', 'email')
    readonly_fields = ('student_id', 'age', 'created_at', 'updated_at')
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'blood_group', 'profile_picture')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'address', 'emergency_contact')
        }),
        ('Academic Information', {
            'fields': ('department', 'enrollment_date', 'graduation_date', 'status')
        }),
        ('System Information', {
            'fields': ('student_id', 'created_at', 'updated_at')
        }),
    )

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'department', 'credit_hours')
    list_filter = ('department', 'credit_hours')
    search_fields = ('code', 'name', 'department__name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'grade', 'enrollment_date')
    list_filter = ('semester', 'grade', 'enrollment_date')
    search_fields = ('student__student_id', 'student__full_name', 'course__code')
    autocomplete_fields = ['student', 'course']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'gpa', 'total_credits', 'earned_credits')
    list_filter = ('semester',)
    search_fields = ('student__student_id', 'student__full_name')