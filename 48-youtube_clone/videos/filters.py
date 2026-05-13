from django_filters import rest_framework as filters
from .models import Video
from django.db.models import Q

class VideoFilter(filters.FilterSet):
    """Filter for videos"""
    min_duration = filters.NumberFilter(field_name='duration', lookup_expr='gte')
    max_duration = filters.NumberFilter(field_name='duration', lookup_expr='lte')
    min_views = filters.NumberFilter(field_name='views', lookup_expr='gte')
    max_views = filters.NumberFilter(field_name='views', lookup_expr='lte')
    published_after = filters.DateTimeFilter(field_name='published_at', lookup_expr='gte')
    published_before = filters.DateTimeFilter(field_name='published_at', lookup_expr='lte')
    
    channel = filters.NumberFilter(field_name='channel__id')
    category = filters.NumberFilter(field_name='category__id')
    privacy = filters.ChoiceFilter(choices=Video.PRIVACY_CHOICES)
    
    keyword = filters.CharFilter(method='filter_keyword')
    
    class Meta:
        model = Video
        fields = ['channel', 'category', 'privacy']
    
    def filter_keyword(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(tags__icontains=value) |
            Q(channel__name__icontains=value)
        )