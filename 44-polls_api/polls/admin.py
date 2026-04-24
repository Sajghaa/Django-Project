from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Poll, Question, Choice, Response, Vote

class ChoiceInlineAdmin(admin.TabularInline):
    model = Choice
    extra = 1

class QuestionInlineAdmin(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True

@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'created_by', 'is_active', 'is_public', 'total_responses', 'created_at']
    list_filter = ['is_active', 'is_public', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['slug', 'total_responses', 'created_at', 'updated_at']
    inlines = [QuestionInlineAdmin]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'poll', 'question_type', 'is_required', 'order_position']
    list_filter = ['question_type', 'is_required']
    search_fields = ['text']
    inlines = [ChoiceInlineAdmin]

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'vote_count', 'order_position']
    list_filter = ['question__poll']
    search_fields = ['text']

@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['poll', 'user', 'ip_address', 'submitted_at']
    list_filter = ['poll', 'submitted_at']
    readonly_fields = ['submitted_at']

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['response', 'question', 'choice', 'text_answer', 'created_at']
    list_filter = ['question']
    readonly_fields = ['created_at']