from django.contrib import admin
from .models import JournalEntry

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'date_created', 'mood']
    list_filter = ['date_created', 'mood', 'author']
    search_fields = ['title', 'content']
    date_hierarchy = 'date_created'