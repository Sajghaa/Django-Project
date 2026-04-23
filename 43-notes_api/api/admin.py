from django.contrib import admin
from .models import Notebook, Tag, Note, Attachment, NoteShare, NoteVersion

@admin.register(Notebook)
class NotebookAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'note_count', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'user__username']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'note_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__username']  # Fixed: added equals sign

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notebook', 'is_favorite', 'is_archived', 'view_count', 'updated_at']
    list_filter = ['is_favorite', 'is_archived', 'is_trash', 'created_at']
    search_fields = ['title', 'content', 'user__username']
    readonly_fields = ['slug', 'content_html', 'view_count', 'created_at', 'updated_at']

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['filename', 'note', 'file_size', 'created_at']
    list_filter = ['created_at']
    search_fields = ['filename', 'note__title']

@admin.register(NoteShare)
class NoteShareAdmin(admin.ModelAdmin):
    list_display = ['note', 'share_token', 'view_count', 'expires_at', 'created_at']
    list_filter = ['created_at']

@admin.register(NoteVersion)
class NoteVersionAdmin(admin.ModelAdmin):
    list_display = ['note', 'version_number', 'created_at']
    list_filter = ['created_at']