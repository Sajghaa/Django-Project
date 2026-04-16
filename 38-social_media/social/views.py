from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import User, Profile, Post, Follow, Like, Comment, Notification
from .forms import RegistrationForm, LoginForm, PostForm, ProfileForm, CommentForm

def home(request):
    """Home page for non-authenticated users"""
    if request.user.is_authenticated:
        return redirect('social:feed')
    return render(request, 'social/home.html')

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('social:feed')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for user
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('social:feed')
    else:
        form = RegistrationForm()
    
    return render(request, 'social/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('social:feed')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}!')
                return redirect('social:feed')
    else:
        form = LoginForm()
    
    return render(request, 'social/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('social:home')

@login_required
def feed(request):
    """Main feed - posts from followed users"""
    # Get users that current user follows
    following_users = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    
    # Get posts from followed users and own posts
    posts = Post.objects.filter(
        Q(user__in=following_users) | Q(user=request.user)
    ).select_related('user', 'user__profile').prefetch_related('likes', 'comments')
    
    # Create post form
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('social:feed')
    else:
        form = PostForm()
    
    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    # Get liked posts for current user
    liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    context = {
        'posts': posts,
        'form': form,
        'liked_posts': liked_posts,
    }
    return render(request, 'social/feed.html', context)

@login_required
def profile(request, username):
    """View user profile"""
    profile_user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    
    # Check if current user follows this profile
    is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    # Get follower/following counts
    followers_count = Follow.objects.filter(following=profile_user).count()
    following_count = Follow.objects.filter(follower=profile_user).count()
    
    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
    }
    return render(request, 'social/profile.html', context)

@login_required
def profile_edit(request):
    """Edit user profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('social:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    
    return render(request, 'social/profile_edit.html', {'form': form})

@login_required
def post_detail(request, post_id):
    """View single post with comments"""
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.filter(parent=None)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            
            # Create notification
            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    from_user=request.user,
                    notification_type='comment',
                    post=post,
                    comment=comment
                )
            
            messages.success(request, 'Comment added!')
            return redirect('social:post_detail', post_id=post.id)
    else:
        form = CommentForm()
    
    liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'is_liked': post.id in liked_posts,
    }
    return render(request, 'social/post_detail.html', context)

@login_required
@require_POST
def like_post(request, post_id):
    """Like or unlike a post (AJAX)"""
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
        post.likes_count -= 1
    else:
        liked = True
        post.likes_count += 1
        
        # Create notification
        if post.user != request.user:
            Notification.objects.create(
                user=post.user,
                from_user=request.user,
                notification_type='like',
                post=post
            )
    
    post.save()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes_count
    })

@login_required
@require_POST
def follow_user(request, username):
    """Follow or unfollow a user (AJAX)"""
    user_to_follow = get_object_or_404(User, username=username)
    
    if user_to_follow == request.user:
        return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
    
    follow, created = Follow.objects.get_or_create(follower=request.user, following=user_to_follow)
    
    if not created:
        follow.delete()
        following = False
        request.user.profile.following_count -= 1
        user_to_follow.profile.followers_count -= 1
    else:
        following = True
        request.user.profile.following_count += 1
        user_to_follow.profile.followers_count += 1
        
        # Create notification
        Notification.objects.create(
            user=user_to_follow,
            from_user=request.user,
            notification_type='follow'
        )
    
    request.user.profile.save()
    user_to_follow.profile.save()
    
    return JsonResponse({
        'following': following,
        'followers_count': user_to_follow.profile.followers_count
    })

@login_required
def explore(request):
    """Explore page - popular posts"""
    posts = Post.objects.all().order_by('-likes_count', '-created_at')[:20]
    
    liked_posts = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    
    context = {
        'posts': posts,
        'liked_posts': liked_posts,
    }
    return render(request, 'social/explore.html', context)

@login_required
def notifications(request):
    """User notifications"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark as read
    notifications.update(is_read=True)
    
    context = {'notifications': notifications}
    return render(request, 'social/notifications.html', context)

@login_required
def followers_list(request, username):
    """List of followers"""
    user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(following=user).select_related('follower')
    
    context = {
        'profile_user': user,
        'users': [f.follower for f in followers],
        'title': 'Followers'
    }
    return render(request, 'social/followers_list.html', context)

@login_required
def following_list(request, username):
    """List of following"""
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(follower=user).select_related('following')
    
    context = {
        'profile_user': user,
        'users': [f.following for f in following],
        'title': 'Following'
    }
    return render(request, 'social/followers_list.html', context)