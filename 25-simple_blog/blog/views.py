from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Post, Category, Comment, Newsletter, Tag, Visitor, PageView
from .forms import PostForm, CommentForm, NewsletterForm, SearchForm

def is_admin(user):
    return user.is_authenticated and user.is_superuser

def track_visitor(request):
    """Track unique visitors"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    visitor, created = Visitor.objects.get_or_create(
        session_key=session_key,
        defaults={
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500]
        }
    )
    
    if not created:
        visitor.visits += 1
        visitor.save()
    
    return visitor

def home(request):
    """Home page with featured posts and latest posts"""
    # Track visitor
    visitor = track_visitor(request)
    
    # Get featured posts (for hero section)
    featured_posts = Post.objects.filter(status='published', featured=True)[:3]
    
    # Get latest posts
    posts = Post.objects.filter(status='published')
    
    # Handle search
    form = SearchForm(request.GET)
    search_query = ''
    selected_category = None
    selected_tag = None
    order_by = '-published_at'
    
    if form.is_valid():
        search_query = form.cleaned_data.get('q')
        selected_category = form.cleaned_data.get('category')
        selected_tag = form.cleaned_data.get('tag')
        order_by = form.cleaned_data.get('order_by', '-published_at')
        
        if search_query:
            posts = posts.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        if selected_category:
            posts = posts.filter(category=selected_category)
        
        if selected_tag:
            posts = posts.filter(tags=selected_tag)
    
    posts = posts.order_by(order_by)
    
    # Pagination
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # Get categories with post counts
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0)
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    ).filter(post_count__gt=0).order_by('-post_count')[:10]
    
    # Newsletter form
    newsletter_form = NewsletterForm()
    
    context = {
        'featured_posts': featured_posts,
        'posts': posts,
        'categories': categories,
        'popular_tags': popular_tags,
        'form': form,
        'search_query': search_query,
        'selected_category': selected_category,
        'selected_tag': selected_tag,
        'newsletter_form': newsletter_form,
    }
    return render(request, 'blog/home.html', context)

def post_detail(request, slug):
    """Single post detail page"""
    post = get_object_or_404(Post, slug=slug, status='published')
    
    # Track view
    visitor = track_visitor(request)
    PageView.objects.create(visitor=visitor, post=post, url=request.path)
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Get comments
    comments = post.comments.filter(parent=None, approved=True)
    
    # Handle comment form
    if request.method == 'POST' and post.allow_comments:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            
            # Check if reply
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = get_object_or_404(Comment, id=parent_id)
            
            comment.save()
            messages.success(request, 'Your comment has been added!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = CommentForm()
    
    # Get related posts (same category or tags)
    related_posts = Post.objects.filter(
        Q(category=post.category) | Q(tags__in=post.tags.all()),
        status='published'
    ).exclude(id=post.id).distinct()[:3]
    
    # Get next and previous posts
    next_post = Post.objects.filter(
        status='published', 
        published_at__gt=post.published_at
    ).order_by('published_at').first()
    
    prev_post = Post.objects.filter(
        status='published', 
        published_at__lt=post.published_at
    ).order_by('-published_at').first()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'related_posts': related_posts,
        'next_post': next_post,
        'prev_post': prev_post,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
@user_passes_test(is_admin)
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
                tag_names = [tag.strip() for tag in tags_input.split(',')]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    post.tags.add(tag)
            
            messages.success(request, f'Post "{post.title}" created successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Create New Post'})

@login_required
@user_passes_test(is_admin)
def post_edit(request, slug):
    """Edit existing post"""
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            updated_post = form.save()
            
            # Update tags
            updated_post.tags.clear()
            tags_input = form.cleaned_data.get('tags_input')
            if tags_input:
                tag_names = [tag.strip() for tag in tags_input.split(',')]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    updated_post.tags.add(tag)
            
            messages.success(request, f'Post "{post.title}" updated successfully!')
            return redirect('blog:post_detail', slug=post.slug)
    else:
        # Pre-populate tags input
        tags_input = ', '.join([tag.name for tag in post.tags.all()])
        form = PostForm(instance=post, initial={'tags_input': tags_input})
    
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Edit Post', 'post': post})

@login_required
@user_passes_test(is_admin)
def post_delete(request, slug):
    """Delete post"""
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.success(request, f'Post "{post_title}" deleted successfully!')
        return redirect('blog:home')
    
    return render(request, 'blog/post_confirm_delete.html', {'post': post})

def category_posts(request, slug):
    """View posts by category"""
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category, status='published')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'category': category,
        'categories': Category.objects.annotate(post_count=Count('posts')),
    }
    return render(request, 'blog/category_posts.html', context)

def tag_posts(request, slug):
    """View posts by tag"""
    tag = get_object_or_404(Tag, slug=slug)
    posts = Post.objects.filter(tags=tag, status='published')
    
    # Pagination
    paginator = Paginator(posts, 6)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'tag': tag,
        'popular_tags': Tag.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0).order_by('-post_count')[:10],
    }
    return render(request, 'blog/tag_posts.html', context)

def about(request):
    """About page"""
    return render(request, 'blog/about.html')

@require_POST
def newsletter_subscribe(request):
    """Subscribe to newsletter"""
    form = NewsletterForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, 'Successfully subscribed to newsletter!')
    else:
        messages.error(request, 'Invalid email address or already subscribed.')
    return redirect(request.META.get('HTTP_REFERER', 'blog:home'))

@require_POST
def like_post(request, slug):
    """Like a post (AJAX)"""
    post = get_object_or_404(Post, slug=slug)
    post.likes += 1
    post.save()
    return JsonResponse({'likes': post.likes})

def search(request):
    """Advanced search page"""
    form = SearchForm(request.GET)
    posts = Post.objects.filter(status='published')
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        tag = form.cleaned_data.get('tag')
        order_by = form.cleaned_data.get('order_by')
        
        if q:
            posts = posts.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(excerpt__icontains=q)
            )
        
        if category:
            posts = posts.filter(category=category)
        
        if tag:
            posts = posts.filter(tags=tag)
        
        if order_by:
            posts = posts.order_by(order_by)
    
    # Pagination
    paginator = Paginator(posts, 12)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'form': form,
        'categories': Category.objects.all(),
        'tags': Tag.objects.annotate(post_count=Count('posts')).filter(post_count__gt=0),
    }
    return render(request, 'blog/search_results.html', context)