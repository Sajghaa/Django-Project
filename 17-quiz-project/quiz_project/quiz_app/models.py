from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Question(models.Model):
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"A: {self.text[:30]}... (Correct: {self.is_correct})"
    
class Result(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerChoices()
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-completed-at']

    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}: {self.score}"
    