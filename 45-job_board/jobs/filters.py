from django_filters import rest_framework as filters
from .models import Job, Company
from django.db.models import Q

class JobFilter(filters.FilterSet):
    """Filter for jobs"""
    keyword = filters.CharFilter(method='filter_keyword')
    category = filters.NumberFilter(field_name='category__id')
    employment_type = filters.ChoiceFilter(choices=Job.EMPLOYMENT_TYPES)
    experience_level = filters.ChoiceFilter(choices=Job.EXPERIENCE_LEVELS)
    remote_type = filters.ChoiceFilter(choices=Job.REMOTE_TYPES)
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    salary_min = filters.NumberFilter(field_name='salary_min', lookup_expr='gte')
    salary_max = filters.NumberFilter(field_name='salary_max', lookup_expr='lte')
    posted_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    posted_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_remote = filters.BooleanFilter(field_name='is_remote')
    
    class Meta:
        model = Job
        fields = ['status']
    
    def filter_keyword(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(company__name__icontains=value)
        )

class CompanyFilter(filters.FilterSet):
    """Filter for companies"""
    industry = filters.ChoiceFilter(choices=Company.INDUSTRY_CHOICES)
    name = filters.CharFilter(lookup_expr='icontains')
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    
    class Meta:
        model = Company
        fields = ['industry', 'size']