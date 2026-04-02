from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    """Custom User Admin for the custom User model"""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_active', 'email_verified', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'email_verified', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {
            'fields': ('phone', 'date_of_birth', 'bio', 'profile_picture')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state', 'country', 'zip_code')
        }),
        ('Social Links', {
            'fields': ('website', 'github', 'linkedin', 'twitter')
        }),
        ('Account Status', {
            'fields': ('email_verified', 'email_verification_token', 'reset_password_token', 'reset_password_token_created')
        }),
        ('Activity Tracking', {
            'fields': ('last_login_ip',),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
    )

admin.site.register(User, CustomUserAdmin)