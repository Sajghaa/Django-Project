from django_filters import rest_framework as filters
from .models import Song, Artist, Album
from django.db.models import Q

class SongFilter(filters.FilterSet):
    """Filter for songs"""
    min_duration = filters.NumberFilter(field_name='duration', lookup_expr='gte')
    max_duration = filters.NumberFilter(field_name='duration', lookup_expr='lte')
    min_play_count = filters.NumberFilter(field_name='play_count', lookup_expr='gte')
    max_play_count = filters.NumberFilter(field_name='play_count', lookup_expr='lte')
    min_likes = filters.NumberFilter(field_name='likes_count', lookup_expr='gte')
    max_likes = filters.NumberFilter(field_name='likes_count', lookup_expr='lte')
    release_after = filters.DateFilter(field_name='release_date', lookup_expr='gte')
    release_before = filters.DateFilter(field_name='release_date', lookup_expr='lte')

    artist = filters.NumberFilter(field_name='artist__id')
    album = filters.NumberFilter(field_name='album__id')
    genre = filters.NumberFilter(field_name='genre__id')
    is_featured = filters.BooleanFilter(field_name='is_featured')
    keyword = filters.CharFilter(method='filter_keyword')

    class Meta:
        model = Song
        fields = ['artist', 'album', 'genre', 'is_featured']

    def filter_keyword(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) |
            Q(artist__name__icontains=value) |
            Q(album__title__icontains=value)
        )

class ArtistFilter(filters.FilterSet):
    """Filter for artists"""
    genre = filters.NumberFilter(field_name='genre__id')
    name_contains = filters.CharFilter(field_name='name', lookup_expr='icontains')
    min_followers = filters.NumberFilter(field_name='followers_count', lookup_expr='gte')
    max_followers = filters.NumberFilter(field_name='followers_count', lookup_expr='lte')

    class Meta:
        model = Artist
        fields = ['genre']

class AlbumFilter(filters.FilterSet):
    """Filter for albums"""
    artist = filters.NumberFilter(field_name='artist__id')
    genre = filters.NumberFilter(field_name='genre__id')
    release_after = filters.DateFilter(field_name='release_date', lookup_expr='gte')
    release_before = filters.DateFilter(field_name='release_date', lookup_expr='lte')
    title_contains = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Album
        fields = ['artist', 'genre']