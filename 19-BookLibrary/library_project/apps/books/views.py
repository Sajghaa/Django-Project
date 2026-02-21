from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.borrows.models import BorrowRecord
from .models import Book


@login_required
def book_list(request):
    """
    Display all books with borrow/return buttons based on user status.
    """

    books = Book.objects.all()

    # Get books currently borrowed by user
    borrowed_book_ids = BorrowRecord.objects.filter(
        user=request.user,
        status=BorrowRecord.Status.BORROWED
    ).values_list("book_id", flat=True)

    # Also track overdue books
    overdue_book_ids = BorrowRecord.objects.filter(
        user=request.user,
        status=BorrowRecord.Status.OVERDUE
    ).values_list("book_id", flat=True)

    return render(
        request,
        "books/book_list.html",
        {
            "books": books,
            "borrowed_book_ids": borrowed_book_ids,
            "overdue_book_ids": overdue_book_ids,
        },
    )