from django.contrib import admin
from .models import URL, Click, UserProfile

@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ['short_code', 'original_url', 'user', 'total_clicks', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['short_code', 'original_url', 'user__username']
    readonly_fields = ['total_clicks', 'unique_clicks', 'created_at', 'updated_at']

@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ['url', 'ip_address', 'country', 'device_type', 'clicked_at']
    list_filter = ['device_type', 'clicked_at']
    search_fields = ['url__short_code', 'ip_address']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_links', 'total_clicks', 'created_at']