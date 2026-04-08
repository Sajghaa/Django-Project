from django_filters import rest_framework as filters
from .models import Post, Category, Tag

class PostFilter(filters.FilterSet):
    """Filter for posts"""
    min_views = filters.NumberFilter(field_name='views', lookup_expr='gte')
    max_views = filters.NumberFilter(field_name='views', lookup_expr='lte')
    min_likes = filters.NumberFilter(field_name='likes', lookup_expr='gte')
    max_likes = filters.NumberFilter(field_name='likes', lookup_expr='lte')
    published_after = filters.DateTimeFilter(field_name='published_at', lookup_expr='gte')
    published_before = filters.DateTimeFilter(field_name='published_at', lookup_expr='lte')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Post
        fields = {
            'status': ['exact'],
            'author': ['exact'],
            'category': ['exact'],
            'tags': ['exact'],
            'title': ['icontains', 'exact'],
            'content': ['icontains'],
        }

class CategoryFilter(filters.FilterSet):
    """Filter for categories"""
    name_contains = filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    class Meta:
        model = Category
        fields = ['name']