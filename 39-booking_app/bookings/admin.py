from django.contrib import admin
from .models import Service, ServiceAvailability, BlockedDate, Booking, Payment, Review

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'service_type', 'price', 'duration', 'capacity', 'is_active']
    list_filter = ['service_type', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ServiceAvailability)
class ServiceAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['service', 'get_day_of_week_display', 'start_time', 'end_time', 'is_available']
    list_filter = ['service', 'day_of_week']

@admin.register(BlockedDate)
class BlockedDateAdmin(admin.ModelAdmin):
    list_display = ['service', 'start_date', 'end_date', 'reason']
    list_filter = ['service']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['booking_number', 'user', 'service', 'start_datetime', 'status', 'total_amount']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['booking_number', 'user__username']
    readonly_fields = ['booking_number', 'created_at', 'updated_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'booking', 'amount', 'payment_method', 'status']
    list_filter = ['payment_method', 'status']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['booking', 'user', 'rating', 'created_at']
    list_filter = ['rating']