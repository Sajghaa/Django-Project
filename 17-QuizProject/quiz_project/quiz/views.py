from django.shortcuts import render, get_object_or_404
from .models import Question

def home(request):

    question_count = Question.objects.count()

    context ={
        'question_count': question_count,
    }

    return render(request, 'quiz/home.html', context)

def question_list(request):

    questions = Question.objects.all()

    context={
        'questions': questions,
        'total': questions.count(),
    }

    return render(request, 'quiz/list.html', context)

def question_detail(request, question_id):

    question = get_object_or_404(Question, id=question_id)
    context ={
        'question': question,
    }

    return render(request, 'quiz/detail.html', context)