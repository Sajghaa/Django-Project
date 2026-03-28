from django.contrib import admin
from .models import Movie, Rating

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ['title', 'genre', 'release_year', 'director', 'average_rating', 'total_reviews']
    list_filter = ['genre', 'release_year']
    search_fields = ['title', 'director', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['movie', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['movie__title', 'user__username']