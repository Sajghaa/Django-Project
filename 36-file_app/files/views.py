from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, Http404, FileResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import File, FileDownload
from .forms import FileUploadForm, ShareFileForm, FilePasswordForm, FileSearchForm
import mimetypes

def home(request):
    """Home page"""
    return render(request, 'files/home.html')

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('files:my_files')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome {user.username}! You can now upload and share files.')
            return redirect('files:my_files')
    else:
        form = UserCreationForm()
    
    return render(request, 'files/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('files:my_files')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('files:my_files')
    else:
        form = AuthenticationForm()
    
    return render(request, 'files/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('files:home')

@login_required
def upload_file(request):
    """Upload a new file"""
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save(commit=False)
            file.uploaded_by = request.user
            file.original_name = request.FILES['file'].name
            
            # Hash password if provided
            if form.cleaned_data.get('password'):
                from django.contrib.auth.hashers import make_password
                file.password = make_password(form.cleaned_data['password'])
            
            file.save()
            
            messages.success(request, f'File "{file.original_name}" uploaded successfully!')
            return redirect('files:file_detail', file_id=file.id)
    else:
        form = FileUploadForm()
    
    return render(request, 'files/upload.html', {'form': form})

@login_required
def my_files(request):
    """List user's uploaded files"""
    files = File.objects.filter(uploaded_by=request.user)
    
    # Search and filter
    form = FileSearchForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        file_type = form.cleaned_data.get('file_type')
        sort_by = form.cleaned_data.get('sort_by')
        
        if q:
            files = files.filter(
                Q(original_name__icontains=q) |
                Q(title__icontains=q) |
                Q(description__icontains=q)
            )
        
        if file_type:
            files = files.filter(file_type=file_type)
        
        if sort_by:
            files = files.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(files, 12)
    page = request.GET.get('page')
    files = paginator.get_page(page)
    
    context = {
        'files': files,
        'form': form,
    }
    return render(request, 'files/my_files.html', context)

@login_required
def shared_with_me(request):
    """Files shared with the user"""
    files = File.objects.filter(
        Q(access_type='shared', allowed_users=request.user) |
        Q(access_type='link')
    ).filter(is_active=True)
    
    # Remove expired files
    files = [f for f in files if not f.is_expired()]
    
    paginator = Paginator(files, 12)
    page = request.GET.get('page')
    files = paginator.get_page(page)
    
    return render(request, 'files/shared_with_me.html', {'files': files})

@login_required
def file_detail(request, file_id):
    """View file details"""
    file = get_object_or_404(File, id=file_id)
    
    # Check access permissions
    if not can_access_file(request.user, file):
        messages.error(request, 'You do not have permission to access this file.')
        return redirect('files:my_files')
    
    context = {
        'file': file,
        'can_download': file.can_download(),
        'share_form': ShareFileForm(),
    }
    return render(request, 'files/file_detail.html', context)

@login_required
def share_file(request, file_id):
    """Share file with other users"""
    file = get_object_or_404(File, id=file_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        form = ShareFileForm(request.POST)
        if form.is_valid():
            usernames = form.cleaned_data['usernames']
            users_added = []
            users_not_found = []
            
            for username in usernames:
                try:
                    user = User.objects.get(username=username)
                    if user != request.user:
                        file.allowed_users.add(user)
                        users_added.append(username)
                except User.DoesNotExist:
                    users_not_found.append(username)
            
            # Update access type to shared
            if file.access_type == 'private':
                file.access_type = 'shared'
                file.save()
            
            if users_added:
                messages.success(request, f'File shared with: {", ".join(users_added)}')
            if users_not_found:
                messages.warning(request, f'Users not found: {", ".join(users_not_found)}')
    
    return redirect('files:file_detail', file_id=file.id)

@login_required
def delete_file(request, file_id):
    """Delete a file"""
    file = get_object_or_404(File, id=file_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        file_name = file.original_name
        file.delete()
        messages.success(request, f'File "{file_name}" deleted successfully.')
        return redirect('files:my_files')
    
    return render(request, 'files/confirm_delete.html', {'file': file})

def download_file(request, file_id):
    """Download a file (with access control)"""
    file = get_object_or_404(File, id=file_id)
    
    # Check if file is active
    if not file.is_active:
        raise Http404("File not available")
    
    # Check expiration
    if file.is_expired():
        raise Http404("File has expired")
    
    # Check download limit
    if file.max_downloads > 0 and file.download_count >= file.max_downloads:
        raise Http404("Download limit reached")
    
    # Check access for private files
    if file.access_type == 'private' and request.user != file.uploaded_by:
        raise Http404("You do not have permission to download this file")
    
    # Check access for shared files
    if file.access_type == 'shared' and request.user != file.uploaded_by and request.user not in file.allowed_users.all():
        raise Http404("You do not have permission to download this file")
    
    # Check password for link files
    if file.access_type == 'link' and file.password:
        if request.method == 'POST':
            form = FilePasswordForm(request.POST)
            if form.is_valid():
                from django.contrib.auth.hashers import check_password
                if check_password(form.cleaned_data['password'], file.password):
                    return serve_file(request, file)
                else:
                    messages.error(request, 'Incorrect password')
        else:
            form = FilePasswordForm()
            return render(request, 'files/password_prompt.html', {'form': form, 'file': file})
    
    return serve_file(request, file)

def serve_file(request, file):
    """Serve the file for download"""
    # Increment download count
    file.download_count += 1
    file.save()
    
    # Track download
    FileDownload.objects.create(
        file=file,
        user=request.user if request.user.is_authenticated else None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
    )
    
    # Serve file
    response = FileResponse(file.file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{file.original_name}"'
    return response

def public_download(request, access_code):
    """Public download via access code"""
    file = get_object_or_404(File, access_code=access_code, is_active=True)
    return download_file(request, file.id)

def can_access_file(user, file):
    """Check if user can access a file"""
    if file.access_type == 'public':
        return True
    elif file.access_type == 'private':
        return user == file.uploaded_by
    elif file.access_type == 'shared':
        return user == file.uploaded_by or user in file.allowed_users.all()
    elif file.access_type == 'link':
        return True
    return False

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



@login_required
def profile(request):
    """User profile page"""
    from django.db.models import Sum
    
    total_downloads = FileDownload.objects.filter(file__uploaded_by=request.user).count()
    total_storage = File.objects.filter(uploaded_by=request.user).aggregate(total=Sum('file_size'))['total'] or 0
    
    context = {
        'total_downloads': total_downloads,
        'public_files': File.objects.filter(uploaded_by=request.user, access_type='public').count(),
        'private_files': File.objects.filter(uploaded_by=request.user, access_type='private').count(),
        'shared_files': File.objects.filter(uploaded_by=request.user, access_type='shared').count(),
        'total_storage': total_storage,
        'recent_downloads': FileDownload.objects.filter(file__uploaded_by=request.user)[:10],
    }
    return render(request, 'files/profile.html', context)

def file_list(request):
    """List all public files"""
    files = File.objects.filter(access_type='public', is_active=True)
    
    # Search and filter
    search_query = request.GET.get('q')
    file_type = request.GET.get('file_type')
    sort_by = request.GET.get('sort', '-created_at')
    
    if search_query:
        files = files.filter(
            Q(original_name__icontains=search_query) |
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if file_type:
        files = files.filter(file_type=file_type)
    
    files = files.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(files, 12)
    page = request.GET.get('page')
    files = paginator.get_page(page)
    
    return render(request, 'files/file_list.html', {'files': files})