from django_filters import rest_framework as filters
from .models import Property
from django.db.models import Q

class PropertyFilter(filters.FilterSet):
    """Filter for properties"""
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_bedrooms = filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')
    min_bathrooms = filters.NumberFilter(field_name='bathrooms', lookup_expr='gte')
    min_square_feet = filters.NumberFilter(field_name='square_feet', lookup_expr='gte')
    max_square_feet = filters.NumberFilter(field_name='square_feet', lookup_expr='lte')
    min_year = filters.NumberFilter(field_name='year_built', lookup_expr='gte')
    max_year = filters.NumberFilter(field_name='year_built', lookup_expr='lte')
    
    property_type = filters.NumberFilter(field_name='property_type__id')
    status = filters.ChoiceFilter(choices=Property.STATUS_CHOICES)
    listing_status = filters.ChoiceFilter(choices=Property.LISTING_STATUS_CHOICES)
    
    features = filters.BaseInFilter(field_name='features__id', lookup_expr='in')
    
    keyword = filters.CharFilter(method='filter_keyword')
    location = filters.CharFilter(method='filter_location')
    
    class Meta:
        model = Property
        fields = ['city', 'state', 'zip_code', 'bedrooms', 'bathrooms']
    
    def filter_keyword(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(description__icontains=value) |
            Q(address__icontains=value)
        )
    
    def filter_location(self, queryset, name, value):
        return queryset.filter(
            Q(city__icontains=value) |
            Q(state__icontains=value) |
            Q(zip_code__icontains=value)
        )