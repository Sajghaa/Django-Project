from django.contrib import admin
from .models import Department, Position, Employee

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']
    prepopulated_fields = {'code': ('name',)}

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'base_salary']
    list_filter = ['department']
    search_fields = ['title']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'email', 'department', 'position', 'employment_status', 'is_active']
    list_filter = ['department', 'position', 'employment_status', 'is_active', 'gender']
    search_fields = ['first_name', 'last_name', 'email', 'employee_id', 'phone']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'gender', 'date_of_birth', 'marital_status')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'zip_code', 'country')
        }),
        ('Employment Information', {
            'fields': ('employee_id', 'department', 'position', 'employment_status', 'hire_date', 'salary', 'manager')
        }),
        ('Qualifications', {
            'fields': ('skills', 'education')
        }),
        ('Profile', {
            'fields': ('profile_picture',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )