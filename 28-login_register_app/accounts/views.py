from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from .forms import (
    RegistrationForm, LoginForm, UserProfileForm, 
    CustomPasswordChangeForm, CustomPasswordResetForm, 
    CustomSetPasswordForm
)
from .models import User

def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.email_verified = False
            user.save()
            
            # Generate email verification token
            token = user.generate_verification_token()
            
            # Send verification email
            verification_url = request.build_absolute_uri(
                reverse('accounts:verify_email', kwargs={'token': token})
            )
            
            send_mail(
                subject='Verify Your Email Address',
                message=f'Hello {user.username},\n\nPlease click the link below to verify your email address:\n\n{verification_url}\n\nThank you for registering!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            
            messages.success(request, 'Registration successful! Please check your email to verify your account.')
            return redirect('accounts:login')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Update last login IP
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    user.last_login_ip = x_forwarded_for.split(',')[0]
                else:
                    user.last_login_ip = request.META.get('REMOTE_ADDR')
                user.save()
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                
                # Redirect to next parameter or dashboard
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')

def verify_email(request, token):
    """Email verification view"""
    user = get_object_or_404(User, email_verification_token=token)
    
    if not user.email_verified:
        user.email_verified = True
        user.email_verification_token = ''
        user.save()
        messages.success(request, 'Your email has been verified! You can now log in.')
    else:
        messages.info(request, 'Your email is already verified.')
    
    return redirect('accounts:login')

@login_required
def dashboard(request):
    """User dashboard view"""
    context = {
        'user': request.user,
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
                
                # Send reset email
                reset_url = request.build_absolute_uri(
                    reverse('accounts:password_reset_confirm', kwargs={'token': token})
                )
                
                send_mail(
                    subject='Password Reset Request',
                    message=f'Hello {user.username},\n\nClick the link below to reset your password:\n\n{reset_url}\n\nThis link expires in 24 hours.\n\nIf you didn\'t request this, please ignore this email.',
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
        # Check if token is expired (24 hours)
        if user.reset_password_token_created:
            time_diff = timezone.now() - user.reset_password_token_created
            if time_diff.total_seconds() > 86400:  # 24 hours
                messages.error(request, 'Password reset link has expired. Please request a new one.')
                return redirect('accounts:password_reset')
    except User.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:password_reset')
    
    if request.method == 'POST':
        form = CustomSetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            # Clear reset token
            user.reset_password_token = ''
            user.reset_password_token_created = None
            user.save()
            messages.success(request, 'Your password has been reset! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomSetPasswordForm(user)
    
    return render(request, 'accounts/password_reset_confirm.html', {'form': form})

def password_reset_complete(request):
    """Password reset complete view"""
    return render(request, 'accounts/password_reset_complete.html')

def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    return render(request, 'accounts/home.html')