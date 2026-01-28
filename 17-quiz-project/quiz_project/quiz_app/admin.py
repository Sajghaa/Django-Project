from django.contrib import admin
from .models import Quiz, Question, Answer, Result

# Simple registration
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Result)

# OR Better: Custom admin for better UI
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at']
    search_fields = ['title']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz']
    list_filter = ['quiz']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['question__quiz', 'is_correct']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'completed_at']
    list_filter = ['quiz', 'completed_at']