from django.db import models
from .models import Category, Tag

def site_info(request):
    """Add site-wide information to all templates"""
    return {
        'categories_nav': Category.objects.all()[:10],
        'popular_tags_nav': Tag.objects.annotate(post_count=models.Count('posts')).filter(
            post_count__gt=0, posts__status='published'
        ).order_by('-post_count')[:15],
    }