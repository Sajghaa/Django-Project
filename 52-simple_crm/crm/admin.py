from django.contrib import admin
from .models import Customer, Interaction, Lead, Opportunity

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'company', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['first_name', 'last_name', 'email', 'company']

@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'type', 'subject', 'date_time', 'user']
    list_filter = ['type', 'date_time']
    search_fields = ['subject', 'description']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'company', 'status', 'created_at']
    list_filter = ['status', 'source']
    search_fields = ['first_name', 'last_name', 'email']

@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'customer', 'amount', 'stage', 'assigned_to']
    list_filter = ['stage', 'assigned_to']
    search_fields = ['name']