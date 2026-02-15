from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.books.models import Book
from .models import BorrowRecord


MAX_BORROWED_BOOKS = 3  # max books a user can borrow at a time


@transaction.atomic
def borrow_book(user, book_id, days=14):
    """
    Borrow a book if:
    - Book has available copies
    - User does not already have an active borrow
    - User has not exceeded max borrowed books
    """

    # Rule 0: Check current borrowed books
    active_borrows = BorrowRecord.objects.filter(
        user=user,
        status=BorrowRecord.Status.BORROWED
    ).count()

    if active_borrows >= MAX_BORROWED_BOOKS:
        raise ValidationError(f"You cannot borrow more than {MAX_BORROWED_BOOKS} books at a time.")

    # Fetch book safely
    try:
        book = Book.objects.select_for_update().get(id=book_id)
    except Book.DoesNotExist:
        raise ValidationError("Book does not exist.")

    # Rule 1: Check availability
    if book.available_copies <= 0:
        raise ValidationError("No copies available.")

    # Rule 2: Prevent double borrowing
    already_borrowed = BorrowRecord.objects.filter(
        user=user,
        book=book,
        status=BorrowRecord.Status.BORROWED
    ).exists()

    if already_borrowed:
        raise ValidationError("You already borrowed this book.")

    # Create borrow record
    due_date = timezone.now().date() + timezone.timedelta(days=days)
    borrow_record = BorrowRecord.objects.create(
        user=user,
        book=book,
        due_date=due_date
    )

    # Reduce available copies
    book.available_copies -= 1
    book.save()

    return borrow_record