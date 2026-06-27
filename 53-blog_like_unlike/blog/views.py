from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from .models import Post, Category, Tag, Comment, Like, UserProfile
from .forms import RegisterForm, PostForm, CommentForm, UserProfileForm, UserEditForm

def home(request):
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    categories = Category.objects.annotate(post_count=Count('post')).filter(post_count__gt=0)
    tags = Tag.objects.annotate(post_count=Count('post')).filter(post_count__gt=0)
    return render(request, 'blog/home.html', {
        'posts': posts,
        'categories': categories,
        'tags': tags,
    })

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug)
    post.views += 1
    post.save()
    comments = post.comments.filter(approved=True)
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = CommentForm()
    user_liked = post.likes.filter(user=request.user).exists() if request.user.is_authenticated else False
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form,
        'user_liked': user_liked,
    })

@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()  # save tags
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm()
    return render(request, 'blog/post_create.html', {'form': form})

@login_required
def post_edit(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', slug=post.slug)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form, 'post': post})

@login_required
def post_delete(request, slug):
    post = get_object_or_404(Post, slug=slug, author=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('home')
    return render(request, 'blog/post_delete_confirm.html', {'post': post})

@login_required
@require_POST
def like_toggle(request, slug):
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count(),
    })

@login_required
@require_POST
def comment_like_toggle(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user in comment.likes.all():
        comment.likes.remove(request.user)
        liked = False
    else:
        comment.likes.add(request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes.count(),
    })

def search(request):
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(author__username__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
        paginator = Paginator(posts, 5)
        page = request.GET.get('page')
        posts = paginator.get_page(page)
        return render(request, 'blog/search.html', {'posts': posts, 'query': query})
    return redirect('home')

def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.post.all()
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/category_posts.html', {'category': category, 'posts': posts})

def tag_posts(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.post_set.all()
    paginator = Paginator(posts, 5)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    return render(request, 'blog/tag_posts.html', {'tag': tag, 'posts': posts})

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(request.GET.get('next', 'home'))
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'blog/login.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def dashboard(request):
    user_posts = request.user.posts.all()
    total_posts = user_posts.count()
    total_comments = request.user.comments.count()
    total_likes_received = Like.objects.filter(post__author=request.user).count()
    recent_posts = user_posts.order_by('-created_at')[:5]
    return render(request, 'blog/dashboard.html', {
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_likes_received': total_likes_received,
        'recent_posts': recent_posts,
    })

@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    return render(request, 'blog/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    })