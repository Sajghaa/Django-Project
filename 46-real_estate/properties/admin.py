from django.contrib import admin
from .models import Agent, PropertyType, PropertyFeature, Property, PropertyImage, Inquiry, SavedProperty, PropertyReview

@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['user', 'company_name', 'phone', 'listing_count', 'rating', 'is_verified']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['user__username', 'company_name', 'license_number']

@admin.register(PropertyType)
class PropertyTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(PropertyFeature)
class PropertyFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['title', 'agent', 'property_type', 'price', 'city', 'status', 'views_count']
    list_filter = ['status', 'listing_status', 'property_type', 'city']
    search_fields = ['title', 'address', 'city', 'zip_code']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views_count', 'inquiries_count', 'created_at', 'updated_at']

@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ['property', 'caption', 'is_primary', 'order_position']
    list_filter = ['is_primary', 'created_at']

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ['property', 'name', 'email', 'inquiry_type', 'status', 'created_at']
    list_filter = ['inquiry_type', 'status', 'created_at']
    search_fields = ['name', 'email', 'message']

@admin.register(SavedProperty)
class SavedPropertyAdmin(admin.ModelAdmin):
    list_display = ['user', 'property', 'created_at']
    list_filter = ['created_at']

@admin.register(PropertyReview)
class PropertyReviewAdmin(admin.ModelAdmin):
    list_display = ['property', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']