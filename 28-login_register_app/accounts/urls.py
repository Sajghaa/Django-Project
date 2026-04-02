from django.urls import path
from django.shortcuts import redirect
from . import views

app_name = 'accounts'

# Add this helper function
def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return redirect('accounts:login')

urlpatterns = [
    # Home page redirect
    path('', home_redirect, name='home'),
    
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('verify-email/<str:token>/', views.verify_email, name='verify_email'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('change-password/', views.change_password, name='change_password'),
    
    # Password Reset URLs
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('password-reset/confirm/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', views.password_reset_complete, name='password_reset_complete'),
]