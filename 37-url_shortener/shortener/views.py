from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseRedirect, Http404
from django.utils import timezone
from django.conf import settings
from .models import URL, Click, UserProfile
from .forms import URLShortenForm, URLSearchForm, PasswordForm, RegistrationForm, LoginForm
from .utils import parse_user_agent, is_unique_click, extract_domain, generate_qr_code
import json

def home(request):
    """Home page with URL shortener form"""
    form = URLShortenForm()
    return render(request, 'shortener/home.html', {'form': form})

@login_required
def create_short_url(request):
    """Create a shortened URL"""
    if request.method == 'POST':
        form = URLShortenForm(request.POST)
        if form.is_valid():
            url = form.save(commit=False)
            url.user = request.user
            url.custom_alias = form.cleaned_data.get('custom_alias')
            
            # Handle password protection
            password = form.cleaned_data.get('password')
            if password:
                from django.contrib.auth.hashers import make_password
                url.password_hash = make_password(password)
            
            url.save()
            
            messages.success(request, f'Short URL created: {url.get_short_url()}')
            return redirect('shortener:url_stats', short_code=url.short_code)
    else:
        form = URLShortenForm()
    
    return render(request, 'shortener/create.html', {'form': form})

def redirect_to_url(request, short_code):
    """Redirect short code to original URL"""
    url = get_object_or_404(URL, short_code=short_code, is_active=True)
    
    # Check expiration
    if url.is_expired():
        url.is_active = False
        url.save()
        raise Http404("This link has expired")
    
    # Check password protection
    if url.password_hash:
        if request.method == 'POST':
            form = PasswordForm(request.POST)
            if form.is_valid():
                from django.contrib.auth.hashers import check_password
                if check_password(form.cleaned_data['password'], url.password_hash):
                    return perform_redirect(request, url)
                else:
                    messages.error(request, 'Incorrect password')
        else:
            form = PasswordForm()
            return render(request, 'shortener/password_prompt.html', {
                'form': form,
                'url': url
            })
    
    return perform_redirect(request, url)

def perform_redirect(request, url):
    """Perform the actual redirect and track analytics"""
    # Track click
    ip = get_client_ip(request)
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    referrer = request.META.get('HTTP_REFERER', '')
    
    # Parse user agent
    ua_info = parse_user_agent(user_agent)
    
    # Check if unique click
    is_unique = is_unique_click(url, ip, session_id)
    
    # Create click record
    click = Click.objects.create(
        url=url,
        ip_address=ip,
        user_agent=user_agent,
        referrer=referrer,
        session_id=session_id,
        device_type=ua_info['device'],
        browser=ua_info['browser'],
        operating_system=ua_info['os']
    )
    
    # Update URL stats
    url.increment_click()
    if is_unique:
        url.unique_clicks += 1
        url.save()
    
    # Update user profile stats
    if url.user and hasattr(url.user, 'profile'):
        url.user.profile.total_clicks += 1
        url.user.profile.save()
    
    # Redirect to original URL
    return HttpResponseRedirect(url.original_url)

@login_required
def dashboard(request):
    """User dashboard showing all shortened URLs"""
    urls = URL.objects.filter(user=request.user)
    
    # Search and filter
    form = URLSearchForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        sort_by = form.cleaned_data.get('sort_by')
        
        if q:
            urls = urls.filter(
                Q(original_url__icontains=q) |
                Q(short_code__icontains=q) |
                Q(title__icontains=q)
            )
        
        if sort_by:
            urls = urls.order_by(sort_by)
        else:
            urls = urls.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(urls, 10)
    page = request.GET.get('page')
    urls = paginator.get_page(page)
    
    # Get total stats
    total_clicks = urls.object_list.aggregate(total=models.Sum('total_clicks'))['total'] or 0
    total_urls = urls.object_list.count()
    
    context = {
        'urls': urls,
        'form': form,
        'total_clicks': total_clicks,
        'total_urls': total_urls,
    }
    return render(request, 'shortener/dashboard.html', context)

@login_required
def url_stats(request, short_code):
    """View analytics for a specific URL"""
    url = get_object_or_404(URL, short_code=short_code, user=request.user)
    
    # Get click statistics
    total_clicks = url.clicks.count()
    unique_clicks = url.unique_clicks
    
    # Get clicks by date (last 7 days)
    from django.db.models.functions import TruncDate
    clicks_by_date = url.clicks.filter(
        clicked_at__gte=timezone.now() - timezone.timedelta(days=30)
    ).annotate(date=TruncDate('clicked_at')).values('date').annotate(count=Count('id')).order_by('date')
    
    dates = [item['date'].strftime('%Y-%m-%d') for item in clicks_by_date]
    counts = [item['count'] for item in clicks_by_date]
    
    # Get top referrers
    top_referrers = url.clicks.values('referrer').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Get top countries
    top_countries = url.clicks.values('country').annotate(count=Count('id')).order_by('-count')[:10]
    
    # Get device breakdown
    devices = url.clicks.values('device_type').annotate(count=Count('id'))
    
    # Get browsers
    browsers = url.clicks.values('browser').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Generate QR code
    qr_code = generate_qr_code(url.get_short_url())
    
    context = {
        'url': url,
        'total_clicks': total_clicks,
        'unique_clicks': unique_clicks,
        'dates': json.dumps(dates),
        'counts': json.dumps(counts),
        'top_referrers': top_referrers,
        'top_countries': top_countries,
        'devices': devices,
        'browsers': browsers,
        'qr_code': qr_code,
    }
    return render(request, 'shortener/analytics.html', context)

@login_required
def delete_url(request, short_code):
    """Delete a shortened URL"""
    url = get_object_or_404(URL, short_code=short_code, user=request.user)
    
    if request.method == 'POST':
        url.delete()
        messages.success(request, 'URL deleted successfully')
        return redirect('shortener:dashboard')
    
    return render(request, 'shortener/confirm_delete.html', {'url': url})

@login_required
def edit_url(request, short_code):
    """Edit URL details"""
    url = get_object_or_404(URL, short_code=short_code, user=request.user)
    
    if request.method == 'POST':
        form = URLShortenForm(request.POST, instance=url)
        if form.is_valid():
            form.save()
            messages.success(request, 'URL updated successfully')
            return redirect('shortener:url_stats', short_code=url.short_code)
    else:
        form = URLShortenForm(instance=url)
    
    return render(request, 'shortener/edit.html', {'form': form, 'url': url})

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('shortener:dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('shortener:dashboard')
    else:
        form = RegistrationForm()
    
    return render(request, 'shortener/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('shortener:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('shortener:dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'shortener/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('shortener:home')

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip