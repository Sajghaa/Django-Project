from datetime import datetime, timedelta
from django.utils import timezone
from .models import Service, ServiceAvailability, BlockedDate, Booking

def get_available_time_slots(service, date, duration_minutes=60):
    """Get available time slots for a service on a given date"""
    
    # Get day of week
    day_of_week = date.weekday()
    
    # Get availability for this day
    try:
        availability = ServiceAvailability.objects.get(
            service=service,
            day_of_week=day_of_week,
            is_available=True
        )
    except ServiceAvailability.DoesNotExist:
        return []
    
    # Check if date is blocked
    is_blocked = BlockedDate.objects.filter(
        service=service,
        start_date__lte=date,
        end_date__gte=date
    ).exists()
    
    if is_blocked:
        return []
    
    # Generate time slots
    slots = []
    current_time = datetime.combine(date, availability.start_time)
    end_time = datetime.combine(date, availability.end_time)
    
    while current_time + timedelta(minutes=duration_minutes) <= end_time:
        # Check if slot is already booked
        is_booked = Booking.objects.filter(
            service=service,
            start_datetime__date=date,
            start_datetime__time=current_time.time(),
            status__in=['pending', 'confirmed']
        ).exists()
        
        if not is_booked:
            slots.append(current_time.time())
        
        current_time += timedelta(minutes=duration_minutes)
    
    return slots

def calculate_total_price(service, guests_count, duration_hours=1):
    """Calculate total price for booking"""
    base_price = service.price
    total = base_price * guests_count
    return total

def is_service_available(service, start_datetime, end_datetime, guests_count):
    """Check if service is available for the requested time slot"""
    
    # Check if within operating hours
    day_of_week = start_datetime.weekday()
    try:
        availability = ServiceAvailability.objects.get(
            service=service,
            day_of_week=day_of_week,
            is_available=True
        )
        if start_datetime.time() < availability.start_time or end_datetime.time() > availability.end_time:
            return False
    except ServiceAvailability.DoesNotExist:
        return False
    
    # Check blocked dates
    is_blocked = BlockedDate.objects.filter(
        service=service,
        start_date__lte=start_datetime.date(),
        end_date__gte=start_datetime.date()
    ).exists()
    
    if is_blocked:
        return False
    
    # Check existing bookings
    overlapping_bookings = Booking.objects.filter(
        service=service,
        start_datetime__lt=end_datetime,
        end_datetime__gt=start_datetime,
        status__in=['pending', 'confirmed']
    ).count()
    
    if overlapping_bookings >= service.capacity:
        return False
    
    return True