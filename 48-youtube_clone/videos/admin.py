from django.contrib import admin
from .models import Channel, Category, Video, Comment, VideoLike, Subscription, Playlist, PlaylistVideo, WatchHistory

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'subscribers', 'total_views', 'created_at']
    search_fields = ['name', 'user__username']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['subscribers', 'total_views']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['title', 'channel', 'views', 'likes', 'privacy', 'created_at']
    list_filter = ['privacy', 'category', 'created_at']
    search_fields = ['title', 'description', 'channel__name']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'likes', 'dislikes', 'comments_count']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['video', 'user', 'content', 'likes', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'user__username', 'video__title']

@admin.register(VideoLike)
class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ['video', 'user', 'value', 'created_at']
    list_filter = ['value', 'created_at']

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['subscriber', 'channel', 'created_at']
    list_filter = ['created_at']

@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'video_count', 'is_public', 'created_at']
    list_filter = ['is_public', 'created_at']

@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'video', 'watched_at', 'progress']
    list_filter = ['watched_at']