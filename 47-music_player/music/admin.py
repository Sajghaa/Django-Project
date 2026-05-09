from django.contrib import admin
from .models import Genre, Artist, Album, Song, Playlist, PlaylistSong, UserFavorite, ListeningHistory, ArtistFollow

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'song_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'monthly_listeners', 'followers_count', 'songs_count', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['monthly_listeners', 'followers_count', 'songs_count']

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'release_date', 'song_count', 'created_at']
    search_fields = ['title', 'artist__name']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['release_date', 'genre']

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'album', 'duration', 'play_count', 'likes_count', 'is_featured']
    search_fields = ['title', 'artist__name']
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ['genre', 'release_date', 'is_featured']
    readonly_fields = ['play_count', 'likes_count', 'created_at', 'updated_at']

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'song_count', 'is_public', 'created_at']
    search_fields = ['name', 'user__username']
    list_filter = ['is_public', 'created_at']

@admin.register(PlaylistSong)
class PlaylistSongAdmin(admin.ModelAdmin):
    list_display = ['playlist', 'song', 'order_position', 'added_at']
    list_filter = ['added_at']

@admin.register(UserFavorite)
class UserFavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'song', 'created_at']
    list_filter = ['created_at']

@admin.register(ListeningHistory)
class ListeningHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'song', 'progress', 'played_at']
    list_filter = ['played_at']

@admin.register(ArtistFollow)
class ArtistFollowAdmin(admin.ModelAdmin):
    list_display = ['user', 'artist', 'created_at']
    list_filter = ['created_at']