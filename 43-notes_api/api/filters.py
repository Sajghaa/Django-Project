from django_filters import rest_framework as filters
from .models import Note, Notebook, Tag

class NoteFilter(filters.FilterSet):
    """Filter for notes"""
    notebook = filters.NumberFilter(field_name='notebook_id')
    tag = filters.NumberFilter(field_name='tags__id')
    is_favorite = filters.BooleanFilter(field_name='is_favorite')
    is_archived = filters.BooleanFilter(field_name='is_archived')
    is_trash = filters.BooleanFilter(field_name='is_trash')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')
    reminder_upcoming = filters.BooleanFilter(method='filter_upcoming_reminders')
    
    class Meta:
        model = Note
        fields = {
            'title': ['icontains', 'exact'],
            'content': ['icontains'],
        }
    
    def filter_upcoming_reminders(self, queryset, name, value):
        if value:
            from django.utils import timezone
            return queryset.filter(
                reminder_date__gte=timezone.now(),
                reminder_date__lte=timezone.now() + timezone.timedelta(days=7)
            )
        return queryset

class NotebookFilter(filters.FilterSet):
    """Filter for notebooks"""
    name_contains = filters.CharFilter(field_name='name', lookup_expr='icontains')
    
    class Meta:
        model = Notebook
        fields = ['name']