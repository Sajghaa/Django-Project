from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from django.db.models import Q, Count
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm,
    CustomPasswordChangeForm, CustomPasswordResetForm, CustomSetPasswordForm
)
from .models import User, LoginHistory
import json

def home(request):
    """Home page view"""
    return render(request, 'accounts/home.html')

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.email_verified = False
            user.save()
            
            # Generate verification token
            token = user.generate_verification_token()
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': token})
            )
            
            send_mail(
                subject='Verify Your Email Address',
                message=f'Hello {user.username or user.email},\n\nPlease click the link below to verify your email address:\n\n{verification_url}\n\nThis link expires in 24 hours.\n\nThank you for registering!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('accounts:email_verification_sent')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Try to authenticate with email or username
            if '@' in username:
                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass
            
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Reset login attempts on successful login
                user.reset_login_attempts()
                
                # Record login history
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                
                LoginHistory.objects.create(
                    user=user,
                    ip_address=ip,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    successful=True
                )
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
        else:
            # Record failed login attempt
            username = request.POST.get('username')
            if username:
                try:
                    if '@' in username:
                        user = User.objects.get(email=username)
                    else:
                        user = User.objects.get(username=username)
                    user.increment_login_attempts()
                except User.DoesNotExist:
                    pass
            messages.error(request, 'Invalid email/username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:home')

def verify_email(request, token):
    """Email verification view"""
    try:
        user = User.objects.get(email_verification_token=token)
        
        if not user.email_verified:
            if user.is_token_valid('verification'):
                user.email_verified = True
                user.email_verification_token = ''
                user.save()
                messages.success(request, 'Your email has been verified! You can now log in.')
            else:
                messages.error(request, 'Verification link has expired. Please request a new one.')
        else:
            messages.info(request, 'Your email is already verified.')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
    
    return redirect('accounts:login')

def email_verification_sent(request):
    """Email verification sent page"""
    return render(request, 'accounts/email_verification_sent.html')

@login_required
def dashboard(request):
    """User dashboard view"""
    # Get user statistics
    context = {
        'user': request.user,
        'recent_logins': request.user.login_history.all()[:5],
    }
    return render(request, 'accounts/dashboard.html', context)

@login_required
def profile_view(request):
    """View user profile"""
    return render(request, 'accounts/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

@login_required
def change_password(request):
    """Change user password"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been changed!')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

def password_reset(request):
    """Password reset request view"""
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = user.generate_reset_token()
                
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'token': token})
                )
                
                send_mail(
                    subject='Password Reset Request',
                    message=f'Hello {user.username or user.email},\n\nClick the link below to reset your password:\n\n{reset_url}\n\nThis link expires in 24 hours.\n\nIf you didn\'t request this, please ignore this email.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
                messages.success(request, 'Password reset link has been sent to your email.')
                return redirect('accounts:password_reset_done')
            except User.DoesNotExist:
                messages.info(request, 'If an account exists with that email, you will receive reset instructions.')
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'accounts/password_reset.html', {'form': form})

def password_reset_done(request):
    """Password reset done view"""
    return render(request, 'accounts/password_reset_done.html')

def password_reset_confirm(request, token):
    """Password reset confirmation view"""
    try:
        user = User.objects.get(reset_password_token=token)
        if not user.is_token_valid('reset'):
            messages.error(request, 'Password reset link has expired. Please request a new one.')
            return redirect('accounts:password_reset')
    except User.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:password_reset')
    
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.reset_password_token = ''
            user.reset_password_token_created = None
            user.save()
            messages.success(request, 'Your password has been reset! You can now log in.')
            return redirect('accounts:password_reset_complete')
    else:
        form = CustomSetPasswordForm(user)
    
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})

def password_reset_complete(request):
    """Password reset complete view"""
    return render(request, 'accounts/password_reset_complete.html')

@login_required
def resend_verification(request):
    """Resend email verification link"""
    user = request.user
    
    if user.email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('accounts:dashboard')
    
    token = user.generate_verification_token()
    verification_url = request.build_absolute_uri(
        reverse('accounts:verify_email', kwargs={'token': token})
    )
    
    send_mail(
        subject='Verify Your Email Address',
        message=f'Hello {user.username or user.email},\n\nPlease click the link below to verify your email address:\n\n{verification_url}\n\nThis link expires in 24 hours.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
    
    messages.success(request, 'Verification email has been sent. Please check your inbox.')
    return redirect('accounts:email_verification_sent')