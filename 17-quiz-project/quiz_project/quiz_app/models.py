# quiz_app/models.py
from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    """
    Represents a quiz/topic
    CRUD: Admin can Create/Read/Update/Delete quizzes
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Question(models.Model):
    """
    Questions belonging to a quiz
    One Quiz → Many Questions
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    
    def __str__(self):
        return f"Q: {self.text[:50]}..."

class Answer(models.Model):

  
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"A: {self.text[:30]}... (Correct: {self.is_correct})"

class Result(models.Model):
    """
    Stores user's quiz attempt results
    One User → Many Results (for different quizzes)
    One Quiz → Many Results (from different users)
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-completed_at']  # Show latest first
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title}: {self.score}"