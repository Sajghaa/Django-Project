from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Skill, Portfolio, Service, Testimonial, BlogPost, ContactMessage, Category, SiteInfo
from .forms import ContactForm, BlogPostForm, PortfolioForm

# Helper function for admin check
def is_admin(user):
    return user.is_authenticated and user.is_superuser

# Home Page View
def home(request):
    """Home page with all sections"""
    # Get all active content
    skills = Skill.objects.filter(is_active=True)
    services = Service.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)
    
    # Get featured and recent portfolio items
    featured_projects = Portfolio.objects.filter(featured=True)[:6]
    recent_projects = Portfolio.objects.all()[:6]
    
    # Get recent blog posts
    recent_posts = BlogPost.objects.filter(published=True)[:3]
    
    # Get site info
    site_info = SiteInfo.objects.first()
    
    context = {
        'skills': skills,
        'services': services,
        'testimonials': testimonials,
        'featured_projects': featured_projects,
        'recent_projects': recent_projects,
        'recent_posts': recent_posts,
        'site_info': site_info,
    }
    return render(request, 'portfolio/index.html', context)

# About Page View
def about(request):
    """About page"""
    skills = Skill.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    
    context = {
        'skills': skills,
        'testimonials': testimonials,
    }
    return render(request, 'portfolio/about.html', context)

# Portfolio Views
def portfolio_list(request):
    """Portfolio gallery page"""
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        portfolios = Portfolio.objects.filter(category=category)
    else:
        portfolios = Portfolio.objects.all()
    
    # Pagination
    paginator = Paginator(portfolios, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'portfolios': page_obj,
        'categories': categories,
        'selected_category': category_slug,
    }
    return render(request, 'portfolio/portfolio_list.html', context)

def portfolio_detail(request, slug):
    """Portfolio detail page"""
    portfolio = get_object_or_404(Portfolio, slug=slug)
    
    # Get related projects (same category)
    related_projects = Portfolio.objects.filter(category=portfolio.category).exclude(id=portfolio.id)[:3]
    
    context = {
        'portfolio': portfolio,
        'related_projects': related_projects,
    }
    return render(request, 'portfolio/portfolio_detail.html', context)

# Service Views
def services(request):
    """Services page"""
    services_list = Service.objects.filter(is_active=True)
    return render(request, 'portfolio/services.html', {'services': services_list})

# Blog Views
class BlogListView(ListView):
    model = BlogPost
    template_name = 'portfolio/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(published=True)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        # Filter by tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_tag'] = self.request.GET.get('tag', '')
        
        # Get all unique tags
        all_posts = BlogPost.objects.filter(published=True)
        tags_set = set()
        for post in all_posts:
            if post.tags:
                for tag in post.tags.split(','):
                    tags_set.add(tag.strip())
        context['all_tags'] = sorted(tags_set)
        
        return context

def blog_detail(request, slug):
    """Blog post detail page"""
    post = get_object_or_404(BlogPost, slug=slug, published=True)
    
    # Increment view count
    post.views += 1
    post.save()
    
    # Get related posts (same tags)
    related_posts = []
    if post.tags:
        tags_list = [tag.strip() for tag in post.tags.split(',')]
        related_posts = BlogPost.objects.filter(
            published=True
        ).exclude(id=post.id)
        
        for tag in tags_list:
            related_posts = related_posts.filter(tags__icontains=tag)
        related_posts = related_posts[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'portfolio/blog_detail.html', context)

# Contact View
def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you! Your message has been sent successfully.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'portfolio/contact.html', {'form': form})

# Admin Views
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard"""
    total_portfolios = Portfolio.objects.count()
    total_blog_posts = BlogPost.objects.count()
    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()
    
    recent_messages = ContactMessage.objects.order_by('-created_at')[:5]
    recent_portfolios = Portfolio.objects.order_by('-created_at')[:5]
    recent_blogs = BlogPost.objects.order_by('-created_at')[:5]
    
    context = {
        'total_portfolios': total_portfolios,
        'total_blog_posts': total_blog_posts,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'recent_messages': recent_messages,
        'recent_portfolios': recent_portfolios,
        'recent_blogs': recent_blogs,
    }
    return render(request, 'portfolio/admin/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def add_blog_post(request):
    """Add new blog post"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_dashboard')
    else:
        form = BlogPostForm()
    
    return render(request, 'portfolio/admin/blog_form.html', {'form': form, 'title': 'Add Blog Post'})

@login_required
@user_passes_test(is_admin)
def edit_blog_post(request, slug):
    """Edit blog post"""
    post = get_object_or_404(BlogPost, slug=slug)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = BlogPostForm(instance=post)
    
    return render(request, 'portfolio/admin/blog_form.html', {'form': form, 'title': 'Edit Blog Post', 'post': post})

@login_required
@user_passes_test(is_admin)
def delete_blog_post(request, slug):
    """Delete blog post"""
    post = get_object_or_404(BlogPost, slug=slug)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Blog post deleted successfully!')
        return redirect('admin_dashboard')
    
    return render(request, 'portfolio/admin/confirm_delete.html', {'object': post, 'type': 'Blog Post'})

@login_required
@user_passes_test(is_admin)
def view_messages(request):
    """View all contact messages"""
    messages_list = ContactMessage.objects.all().order_by('-created_at')
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        msg = get_object_or_404(ContactMessage, id=request.GET.get('mark_read'))
        msg.is_read = True
        msg.save()
        messages.success(request, 'Message marked as read.')
        return redirect('view_messages')
    
    paginator = Paginator(messages_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'portfolio/admin/messages.html', {'messages': page_obj})