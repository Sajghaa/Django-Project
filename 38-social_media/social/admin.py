from django.contrib import admin
from .models import Profile, Post, Follow, Like, Comment, Notification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'followers_count', 'following_count', 'posts_count']
    search_fields = ['user__username']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'content', 'likes_count', 'comments_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'content']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'created_at']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'content', 'created_at']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'from_user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']