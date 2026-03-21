from django.contrib import admin
from .models import Subscriber, Newsletter, NewsletterClick, NewsletterOpen

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['confirmation_token', 'confirmed_at', 'unsubscribed_at']
    actions = ['send_confirmation']
    
    def send_confirmation(self, request, queryset):
        for subscriber in queryset:
            if subscriber.status == 'pending':
                subscriber.send_confirmation_email()
        self.message_user(request, f'Confirmation emails sent to {queryset.count()} subscribers.')
    send_confirmation.short_description = "Send confirmation emails to selected subscribers"

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'sent_to_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject']
    readonly_fields = ['sent_to_count', 'opened_count', 'clicked_count', 'sent_at']

@admin.register(NewsletterClick)
class NewsletterClickAdmin(admin.ModelAdmin):
    list_display = ['newsletter', 'subscriber', 'url', 'clicked_at']
    list_filter = ['clicked_at']

@admin.register(NewsletterOpen)
class NewsletterOpenAdmin(admin.ModelAdmin):
    list_display = ['newsletter', 'subscriber', 'opened_at']
    list_filter = ['opened_at']