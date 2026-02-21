from django.shortcuts import redirect,render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import BorrowRecord
from .services import borrow_book, return_book


@login_required
def borrow_book_view(request, book_id):
    try:
        borrow_book(user=request.user, book_id=book_id)
        messages.success(request, "Book borrowed successfully.")
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect("book_list")


@login_required
def return_book_view(request, book_id):
    try:
        return_book(user=request.user, book_id=book_id)
        messages.success(request, "Book returned successfully.")
    except ValidationError as e:
        messages.error(request, e.message)

    return redirect("book_list")

@login_required
def dashboard(request):
    borrowed_records = BorrowRecord.objects.filter(
        user=request.user,
        status=BorrowRecord.Status.BORROWED
    )

    # Automatically update overdue status
    for record in borrowed_records:
        if record.is_overdue:
            record.status = BorrowRecord.Status.OVERDUE
            record.save()

    borrowed_records = BorrowRecord.objects.filter(
        user=request.user
    )

    return render(
        request,
        "core/dashboard.html",
        {"borrowed_books": borrowed_records},
    )