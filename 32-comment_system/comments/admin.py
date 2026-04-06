from django.contrib import admin
from .models import Comment, CommentLike, CommentReport, CommentSubscription

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content_type', 'object_id', 'status', 'likes', 'reports', 'created_at']
    list_filter = ['status', 'created_at', 'content_type']
    search_fields = ['author__username', 'content', 'moderation_note']
    readonly_fields = ['created_at', 'updated_at', 'user_ip', 'user_agent']
    list_editable = ['status']
    
    fieldsets = (
        ('Content', {
            'fields': ('author', 'content_type', 'object_id', 'content', 'content_html')
        }),
        ('Status', {
            'fields': ('status', 'moderator', 'moderation_note', 'moderated_at')
        }),
        ('Statistics', {
            'fields': ('likes', 'reports', 'is_edited')
        }),
        ('Metadata', {
            'fields': ('user_ip', 'user_agent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_comments', 'mark_as_spam', 'delete_comments']
    
    def approve_comments(self, request, queryset):
        for comment in queryset:
            comment.approve(request.user)
        self.message_user(request, f'{queryset.count()} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def mark_as_spam(self, request, queryset):
        for comment in queryset:
            comment.mark_as_spam(request.user)
        self.message_user(request, f'{queryset.count()} comments marked as spam.')
    mark_as_spam.short_description = 'Mark selected comments as spam'
    
    def delete_comments(self, request, queryset):
        for comment in queryset:
            comment.delete_comment(request.user)
        self.message_user(request, f'{queryset.count()} comments deleted.')
    delete_comments.short_description = 'Delete selected comments'

@admin.register(CommentLike)
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ['comment', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'comment__content']

@admin.register(CommentReport)
class CommentReportAdmin(admin.ModelAdmin):
    list_display = ['comment', 'reporter', 'reason', 'resolved', 'created_at']
    list_filter = ['reason', 'resolved', 'created_at']
    search_fields = ['reporter__username', 'comment__content', 'details']
    list_editable = ['resolved']

@admin.register(CommentSubscription)
class CommentSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_type', 'object_id', 'subscribed_at']
    list_filter = ['subscribed_at']
    search_fields = ['user__username']