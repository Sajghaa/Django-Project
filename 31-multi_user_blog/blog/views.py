from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from .models import Post, Category, Tag, Comment, Like, Bookmark, Profile
from .forms import RegistrationForm, LoginForm, PostForm, CommentForm, ProfileForm, UserEditForm

def is_author(user):
    return user.is_authenticated and hasattr(user, 'profile') and user.profile.is_author

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin'))

def home(request):
    """Home page with featured and latest posts"""
    featured_posts = Post.objects.filter(status='published', featured=True)[:3]
    latest_posts = Post.objects.filter(status='published')[:6]
    
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)[:5]
    
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')[:10]
    
    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'categories': categories,
        'popular_tags': popular_tags,
    }
    return render(request, 'blog/home.html', context)

def post_list(request):
    """List all published posts"""
    posts = Post.objects.filter(status='published')
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    # Tag filter
    tag_slug = request.GET.get('tag')
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags=tag)
    
    # Author filter
    author_username = request.GET.get('author')
    if author_username:
        posts = posts.filter(author__username=author_username)
    
    # Pagination
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)
    
    context = {
        'posts': posts,
        'categories': categories,
        'search_query': search_query,
        'category_slug': category_slug,
        'tag_slug': tag_slug,
        'author_username': author_username,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    """Display single post"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Comments
    comments = post.comments.filter(parent=None, approved=True)
    
    # Handle comment form
    if request.method == 'POST' and request.user.is_authenticated:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = CommentForm()
    
    # Check if user liked the post
    user_liked = False
    user_bookmarked = False
    if request.user.is_authenticated:
        user_liked = Like.objects.filter(user=request.user, post=post).exists()
        user_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()
    
    # Related posts
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
        'user_bookmarked': user_bookmarked,
    }
    return render(request, 'blog/post_detail.html', context)

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('blog:home')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            Profile.objects.create(user=user, role=role)
            login(request, user)
            messages.success(request, f'Welcome {user.username}! You are now registered as a {role}.')
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
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'blog:home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    
    return render(request, 'blog/login.html', {'form': form})

@login_required
def user_logout(request):
    """User logout"""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('blog:home')

@login_required
@user_passes_test(is_author)
def my_posts(request):
    """Show user's own posts"""
    posts = Post.objects.filter(author=request.user)
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'posts': posts,
        'total_posts': Post.objects.filter(author=request.user).count(),
        'published_posts': Post.objects.filter(author=request.user, status='published').count(),
        'draft_posts': Post.objects.filter(author=request.user, status='draft').count(),
    }
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
            
            messages.success(request, f'Post "{post.title}" created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create New Post'})

@login_required
def post_edit(request, slug):
    """Edit existing post"""
    post = get_object_or_404(Post, slug=slug)
    
    # Check permission
    if post.author != request.user and not request.user.profile.can_edit_all_posts:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('blog:post_detail', slug=post.slug)
    
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
            
            messages.success(request, f'Post "{post.title}" updated successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        tags_input = ', '.join([tag.name for tag in post.tags.all()])
        form = PostForm(instance=post, initial={'tags_input': tags_input})
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post', 'post': post})

@login_required
def post_delete(request, slug):
    """Delete post"""
    post = get_object_or_404(Post, slug=slug)
    
    if post.author != request.user and not request.user.profile.can_edit_all_posts:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('blog:post_detail', slug=post.slug)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" deleted successfully!')
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
    else:
        liked = True
    
    post.likes = post.post_likes.count()
    post.save()
    
    return JsonResponse({'liked': liked, 'likes_count': post.likes})

@login_required
def bookmark_post(request, slug):
    """Bookmark/unbookmark a post (AJAX)"""
    post = get_object_or_404(Post, slug=slug)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    
    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
    
    return JsonResponse({'bookmarked': bookmarked})

@login_required
def my_bookmarks(request):
    """Show user's bookmarked posts"""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post')
    
    paginator = Paginator(bookmarks, 10)
    page = request.GET.get('page')
    bookmarks = paginator.get_page(page)
    
    return render(request, 'blog/my_bookmarks.html', {'bookmarks': bookmarks})

@login_required
def dashboard(request):
    """User dashboard"""
    user_stats = {
        'total_posts': Post.objects.filter(author=request.user).count(),
        'published_posts': Post.objects.filter(author=request.user, status='published').count(),
        'draft_posts': Post.objects.filter(author=request.user, status='draft').count(),
        'total_comments': Comment.objects.filter(author=request.user).count(),
        'total_likes_received': Like.objects.filter(post__author=request.user).count(),
        'total_views': Post.objects.filter(author=request.user).aggregate(total=models.Sum('views'))['total'] or 0,
    }
    
    recent_posts = Post.objects.filter(author=request.user)[:5]
    recent_comments = Comment.objects.filter(author=request.user)[:5]
    
    context = {
        'user_stats': user_stats,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
    }
    return render(request, 'blog/dashboard.html', context)

@login_required
def profile_view(request):
    """View user profile"""
    return render(request, 'blog/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    """Edit user profile"""
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('blog:profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'blog/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })