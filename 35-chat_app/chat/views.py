from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import ChatRoom, Message, UserProfile, UserStatus
from .forms import RegistrationForm, ChatRoomForm, ProfileForm

def home(request):
    """Home page"""
    if request.user.is_authenticated:
        return redirect('chat:index')
    return render(request, 'chat/home.html')

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('chat:index')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            UserStatus.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('chat:index')
    else:
        form = RegistrationForm()
    
    return render(request, 'chat/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('chat:index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back {username}!')
            return redirect('chat:index')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'chat/login.html')

@login_required
def user_logout(request):
    """User logout"""
    # Update user status
    if hasattr(request.user, 'status'):
        request.user.status.is_online = False
        request.user.status.save()
    
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('chat:home')

@login_required
def index(request):
    """Chat index page with room list"""
    # Update user status
    if hasattr(request.user, 'status'):
        request.user.status.is_online = True
        request.user.status.save()
    
    # Get user's rooms
    my_rooms = request.user.chat_rooms.all()
    public_rooms = ChatRoom.objects.filter(room_type='public').exclude(participants=request.user)
    
    context = {
        'my_rooms': my_rooms,
        'public_rooms': public_rooms,
    }
    return render(request, 'chat/index.html', context)

@login_required
def room_detail(request, slug):
    """Chat room detail"""
    room = get_object_or_404(ChatRoom, slug=slug)
    
    # Add user to participants if not already
    if request.user not in room.participants.all():
        room.participants.add(request.user)
    
    # Get messages
    messages_list = room.messages.all()[:50]
    
    context = {
        'room': room,
        'messages': messages_list,
    }
    return render(request, 'chat/room.html', context)

@login_required
def create_room(request):
    """Create new chat room"""
    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            room.save()
            room.participants.add(request.user)
            messages.success(request, f'Room "{room.name}" created!')
            return redirect('chat:room', slug=room.slug)
    else:
        form = ChatRoomForm()
    
    return render(request, 'chat/create_room.html', {'form': form})

@login_required
def room_list(request):
    """List all public rooms"""
    rooms = ChatRoom.objects.filter(room_type='public', is_active=True)
    return render(request, 'chat/room_list.html', {'rooms': rooms})

@login_required
def profile(request):
    """User profile"""
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('chat:profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'chat/profile.html', {'form': form})

@login_required
def join_room(request, slug):
    """Join a public room"""
    room = get_object_or_404(ChatRoom, slug=slug)
    if request.user not in room.participants.all():
        room.participants.add(request.user)
        messages.success(request, f'You joined {room.name}!')
    return redirect('chat:room', slug=slug)

@login_required
def leave_room(request, slug):
    """Leave a room"""
    room = get_object_or_404(ChatRoom, slug=slug)
    if request.user in room.participants.all():
        room.participants.remove(request.user)
        messages.info(request, f'You left {room.name}')
    return redirect('chat:index')