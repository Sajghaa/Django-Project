from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Service, Booking, Review, Payment
from .forms import BookingForm, ReviewForm, ServiceFilterForm, DateAvailabilityForm
from .utils import get_available_time_slots, calculate_total_price, is_service_available

def home(request):
    """Home page"""
    featured_services = Service.objects.filter(is_active=True)[:6]
    context = {
        'featured_services': featured_services,
    }
    return render(request, 'bookings/home.html', context)

def service_list(request):
    """List all services"""
    services = Service.objects.filter(is_active=True)
    
    # Filter form
    form = ServiceFilterForm(request.GET)
    if form.is_valid():
        service_type = form.cleaned_data.get('service_type')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        search = form.cleaned_data.get('search')
        
        if service_type:
            services = services.filter(service_type=service_type)
        if min_price:
            services = services.filter(price__gte=min_price)
        if max_price:
            services = services.filter(price__lte=max_price)
        if search:
            services = services.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
    
    # Pagination
    paginator = Paginator(services, 12)
    page = request.GET.get('page')
    services = paginator.get_page(page)
    
    context = {
        'services': services,
        'form': form,
    }
    return render(request, 'bookings/service_list.html', context)

def service_detail(request, slug):
    """Service detail page"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    
    # Check if user can review (has completed booking)
    can_review = False
    if request.user.is_authenticated:
        can_review = Booking.objects.filter(
            user=request.user,
            service=service,
            status='completed',
            review__isnull=True
        ).exists()
    
    # Get reviews
    reviews = Review.objects.filter(booking__service=service)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Availability form
    availability_form = DateAvailabilityForm()
    
    context = {
        'service': service,
        'reviews': reviews[:5],
        'avg_rating': avg_rating,
        'reviews_count': reviews.count(),
        'can_review': can_review,
        'availability_form': availability_form,
    }
    return render(request, 'bookings/service_detail.html', context)

@login_required
def check_availability(request, service_id):
    """AJAX endpoint to check availability"""
    service = get_object_or_404(Service, id=service_id)
    date = request.GET.get('date')
    guests = int(request.GET.get('guests', 1))
    
    from datetime import datetime
    booking_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    # Get available time slots
    slots = get_available_time_slots(service, booking_date, service.duration)
    
    # Format slots for JSON
    slots_formatted = [slot.strftime('%H:%M') for slot in slots]
    
    return JsonResponse({
        'available': len(slots) > 0,
        'slots': slots_formatted,
        'message': f'{len(slots)} time slots available' if slots else 'No available slots for this date'
    })

@login_required
def book_service(request, service_id):
    """Book a service"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            start_datetime = form.cleaned_data['start_datetime']
            guests_count = form.cleaned_data['guests_count']
            special_requests = form.cleaned_data['special_requests']
            
            # Calculate end datetime
            end_datetime = start_datetime + timedelta(minutes=service.duration)
            
            # Check availability
            if not is_service_available(service, start_datetime, end_datetime, guests_count):
                messages.error(request, 'This time slot is no longer available')
                return redirect('bookings:service_detail', slug=service.slug)
            
            # Calculate total price
            total_amount = calculate_total_price(service, guests_count, service.duration / 60)
            
            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                service=service,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                guests_count=guests_count,
                special_requests=special_requests,
                total_amount=total_amount,
                deposit_amount=total_amount * 0.3 if total_amount > 500 else 0,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
            )
            
            messages.success(request, f'Booking created! Booking number: {booking.booking_number}')
            return redirect('bookings:booking_confirmation', booking_id=booking.id)
    else:
        # Pre-fill form with GET parameters
        initial_data = {}
        date = request.GET.get('date')
        time = request.GET.get('time')
        guests = request.GET.get('guests', 1)
        
        if date and time:
            from datetime import datetime
            start_datetime = datetime.strptime(f"{date} {time}", '%Y-%m-%d %H:%M')
            initial_data['start_datetime'] = start_datetime
            initial_data['guests_count'] = guests
        
        form = BookingForm(initial=initial_data)
    
    context = {
        'service': service,
        'form': form,
    }
    return render(request, 'bookings/booking_form.html', context)

@login_required
def booking_confirmation(request, booking_id):
    """Booking confirmation page"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_confirmation.html', {'booking': booking})

@login_required
def my_bookings(request):
    """User's bookings list"""
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        bookings = bookings.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(bookings, 10)
    page = request.GET.get('page')
    bookings = paginator.get_page(page)
    
    context = {
        'bookings': bookings,
        'status_filter': status_filter,
    }
    return render(request, 'bookings/my_bookings.html', context)

@login_required
def booking_detail(request, booking_id):
    """Booking detail page"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if user can review
    can_review = booking.status == 'completed' and not hasattr(booking, 'review')
    
    context = {
        'booking': booking,
        'can_review': can_review,
    }
    return render(request, 'bookings/booking_detail.html', context)

@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        # Check if cancellation is allowed (e.g., at least 24 hours before)
        if booking.start_datetime > timezone.now() + timedelta(hours=24):
            booking.status = 'cancelled'
            booking.cancelled_at = timezone.now()
            booking.save()
            messages.success(request, 'Booking cancelled successfully')
        else:
            messages.error(request, 'Cannot cancel booking less than 24 hours before start time')
        
        return redirect('bookings:my_bookings')
    
    return render(request, 'bookings/cancel_booking.html', {'booking': booking})

@login_required
def add_review(request, booking_id):
    """Add a review for a completed booking"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='completed')
    
    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.error(request, 'You have already reviewed this booking')
        return redirect('bookings:booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you for your review!')
            return redirect('bookings:service_detail', slug=booking.service.slug)
    else:
        form = ReviewForm()
    
    return render(request, 'bookings/review_form.html', {'form': form, 'booking': booking})

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('bookings:home')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('bookings:home')
    else:
        form = UserCreationForm()
    
    return render(request, 'bookings/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('bookings:home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}!')
                return redirect('bookings:home')
    else:
        form = AuthenticationForm()
    
    return render(request, 'bookings/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('bookings:home')

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip