from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'skill_level', 'date_joined')
    list_filter = ('skill_level', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('bio', 'avatar', 'favorite_cuisines', 'skill_level')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('bio', 'avatar', 'favorite_cuisines', 'skill_level')}),
    )

admin.site.register(User, CustomUserAdmin)