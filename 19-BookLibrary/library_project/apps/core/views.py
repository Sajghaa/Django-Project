from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.borrows.models import BorrowRecord


@login_required
def dashboard(request):
    borrowed_books = BorrowRecord.objects.filter(
        user=request.user,
        status=BorrowRecord.Status.BORROWED
    )

    return render(
        request,
        "core/dashboard.html",
        {"borrowed_books": borrowed_books},
    )