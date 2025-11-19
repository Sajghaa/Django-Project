from django.shortcuts import render
from .forms import FeedbackForm

def feedback_view(request):
    success = False

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            success = True
            form = FeedbackForm()  # reset form after success
    else:
        form = FeedbackForm()

    return render(request, "feedback/form.html", {"form": form, "success": success})
