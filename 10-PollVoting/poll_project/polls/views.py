from django.shortcuts import render, get_object_or_404, redirect
from .models import Question, Choice

def home(request):
    questions = Question.objects.all()
    return render(request, "polls/home.html", {"questions": questions})


def vote(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    if request.method == "POST":
        selected_choice_id = request.POST.get("choice")
        if selected_choice_id:
            choice = Choice.objects.get(id=selected_choice_id)
            choice.votes += 1
            choice.save()
            return redirect("results", question_id=question.id)

    return render(request, "polls/vote.html", {"question": question})


def results(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    return render(request, "polls/results.html", {"question": question})
