from django.contrib import admin
from .models import Todo, Category, TodoHistory

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'due_date', 'created_at']
    list_filter = ['priority', 'status', 'user']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['user']
    search_fields = ['name']

@admin.register(TodoHistory)
class TodoHistoryAdmin(admin.ModelAdmin):
    list_display = ['todo', 'action', 'user', 'created_at']
    list_filter = ['action', 'user']
    readonly_fields = ['created_at']