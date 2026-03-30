from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Category, Comment, Newsletter, Tag, Visitor, PageView

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'post_count', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Posts'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'views', 'likes', 'featured', 'published_at']
    list_filter = ['status', 'category', 'tags', 'featured', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'likes', 'created_at', 'updated_at', 'reading_time_display']
    date_hierarchy = 'published_at'
    filter_horizontal = ['tags']
    list_editable = ['status', 'featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'category', 'tags', 'status', 'featured')
        }),
        ('Content', {
            'fields': ('content', 'excerpt', 'featured_image')
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('allow_comments',)
        }),
        ('Statistics', {
            'fields': ('views', 'likes', 'created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def reading_time_display(self, obj):
        return f"{obj.reading_time} min"
    reading_time_display.short_description = 'Reading Time'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['name', 'post', 'content_preview', 'approved', 'created_at']
    list_filter = ['approved', 'created_at']
    search_fields = ['name', 'email', 'content']
    list_editable = ['approved']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']

@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'visits', 'first_visit', 'last_visit']
    readonly_fields = ['session_key', 'ip_address', 'user_agent', 'first_visit', 'last_visit', 'visits']
    list_filter = ['first_visit']

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['visitor', 'post', 'url', 'viewed_at']
    readonly_fields = ['visitor', 'post', 'url', 'viewed_at']
    list_filter = ['viewed_at']