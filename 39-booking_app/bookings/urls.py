from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Services
    path('services/', views.service_list, name='service_list'),
    path('service/<slug:slug>/', views.service_detail, name='service_detail'),
    
    # Booking
    path('book/<int:service_id>/', views.book_service, name='book_service'),
    path('booking/confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking/<int:booking_id>/review/', views.add_review, name='add_review'),
    
    # User Bookings
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('booking/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    
    # API
    path('api/availability/<int:service_id>/', views.check_availability, name='check_availability'),
]