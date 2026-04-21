from .models import Category, Tag

def blog_context(request):
    """Add common data to all templates"""
    categories = Category.objects.filter(post_count__gt=0)[:10]
    tags = Tag.objects.filter(post_count__gt=0).order_by('-post_count')[:15]
    
    return {
        'all_categories': categories,
        'popular_tags': tags,
    }