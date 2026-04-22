from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from .models import Post, Category, Tag, Comment, Like, UserProfile
from .forms import RegistrationForm, LoginForm, PostForm, CommentForm, SearchForm

def is_author(user):
    return user.is_authenticated and user.is_staff

def home(request):
    """Homepage with featured and latest posts"""
    featured_posts = Post.objects.filter(status='published', featured=True)[:3]
    latest_posts = Post.objects.filter(status='published')[:6]
    
    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
    }
    return render(request, 'blog/home.html', context)
    
def post_list(request):
    """List all published posts"""
    posts = Post.objects.filter(status='published')
    
    # Search and filter
    form = SearchForm(request.GET)
    search_query = None
    selected_category = None
    selected_tag = None
    sort_by = request.GET.get('sort_by', '-published_at')  # Default value
    
    if form.is_valid():
        search_query = form.cleaned_data.get('q')
        selected_category = form.cleaned_data.get('category')
        selected_tag = form.cleaned_data.get('tag')
        sort_by = form.cleaned_data.get('sort_by') or '-published_at'  # Handle None
        
        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        if selected_category:
            posts = posts.filter(category=selected_category)
        
        if selected_tag:
            posts = posts.filter(tags=selected_tag)
    
    # Ensure sort_by is valid
    valid_sort_fields = ['-published_at', 'published_at', '-views', '-likes', 'title']
    if sort_by not in valid_sort_fields:
        sort_by = '-published_at'
    
    posts = posts.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'form': form,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_tag': selected_tag,
    }
    return render(request, 'blog/post_list.html', context)
def post_detail(request, slug):
    """Single post detail view"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Comments
    comments = post.comments.filter(parent=None, approved=True)
    
    # Comment form
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = CommentForm()
    
    # Check if user liked
    user_liked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, post=post).exists()
    
    # Related posts (same category or tags)
    related_posts = Post.objects.filter(
        Q(category=post.category) | Q(tags__in=post.tags.all()),
        status='published'
    ).exclude(id=post.id).distinct()[:3]
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'related_posts': related_posts,
        'user_liked': user_liked,
    }
    return render(request, 'blog/post_detail.html', context)

def category_posts(request, slug):
    """Posts by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published')
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category_posts.html', context)

def tag_posts(request, slug):
    """Posts by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, status='published')
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'tag': tag,
        'posts': posts,
    }
    return render(request, 'blog/tag_posts.html', context)

def author_posts(request, username):
    """Posts by author"""
    from django.contrib.auth.models import User
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=author, status='published')
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'author': author,
        'posts': posts,
    }
    return render(request, 'blog/author_posts.html', context)

def search_results(request):
    """Search results page"""
    query = request.GET.get('q', '')
    posts = Post.objects.filter(status='published')
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'query': query,
        'posts': posts,
    }
    return render(request, 'blog/search_results.html', context)

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('blog:home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome {user.username}!')
            return redirect('blog:home')
    else:
        form = RegistrationForm()
    
    return render(request, 'blog/register.html', {'form': form})

def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('blog:home')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back {username}!')
                return redirect('blog:home')
    else:
        form = LoginForm()
    
    return render(request, 'blog/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out')
    return redirect('blog:home')

@login_required
@user_passes_test(is_author)
def dashboard(request):
    """Author dashboard"""
    total_posts = Post.objects.filter(author=request.user).count()
    published_posts = Post.objects.filter(author=request.user, status='published').count()
    draft_posts = Post.objects.filter(author=request.user, status='draft').count()
    total_comments = Comment.objects.filter(post__author=request.user).count()
    total_views = Post.objects.filter(author=request.user).aggregate(total=models.Sum('views'))['total'] or 0
    
    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'total_comments': total_comments,
        'total_views': total_views,
    }
    return render(request, 'blog/dashboard.html', context)

@login_required
@user_passes_test(is_author)
def my_posts(request):
    """List user's posts"""
    posts = Post.objects.filter(author=request.user)
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {'posts': posts}
    return render(request, 'blog/my_posts.html', context)

@login_required
@user_passes_test(is_author)
def post_create(request):
    """Create new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Handle tags
            tags_input = form.cleaned_data.get('tags_input')
            if tags_input:
                tag_names = [tag.strip().lower() for tag in tags_input.split(',')]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
            
            messages.success(request, f'Post "{post.title}" created!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create New Post'})

@login_required
@user_passes_test(is_author)
def post_edit(request, slug):
    """Edit post"""
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save()
            
            # Update tags
            updated_post.tags.clear()
            tags_input = form.cleaned_data.get('tags_input')
            if tags_input:
                tag_names = [tag.strip().lower() for tag in tags_input.split(',')]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    updated_post.tags.add(tag)
            
            messages.success(request, f'Post "{post.title}" updated!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        tags_input = ', '.join([tag.name for tag in post.tags.all()])
        form = PostForm(instance=post, initial={'tags_input': tags_input})
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post', 'post': post})

@login_required
@user_passes_test(is_author)
def post_delete(request, slug):
    """Delete post"""
    post = get_object_or_404(Post, slug=slug, author=request.user)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" deleted!')
        return redirect('blog:my_posts')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

@login_required
def like_post(request, slug):
    """Like/unlike a post (AJAX)"""
    post = get_object_or_404(Post, slug=slug)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        like.delete()
        liked = False
        post.likes -= 1
    else:
        liked = True
        post.likes += 1
    
    post.save()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes
    })