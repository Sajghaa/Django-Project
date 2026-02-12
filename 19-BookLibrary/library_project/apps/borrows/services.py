from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.books.models import Book
from .models import BorrowRecord


@transaction.atomic
def borrow_book(user, book_id, days=14):
    """
    Borrow a book if:
    - Book has available copies
    - User does not already have an active borrow
    """

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

@transaction.atomic
def return_book(user, book_id):
    """
    Return a borrowed book.
    """

    try:
        borrow_record = BorrowRecord.objects.select_for_update().get(
            user=user,
            book_id=book_id,
            status=BorrowRecord.Status.BORROWED
        )
    except BorrowRecord.DoesNotExist:
        raise ValidationError("No active borrow found.")

    book = borrow_record.book

    # Mark returned
    borrow_record.mark_as_returned()

    # Increase available copies
    book.available_copies += 1
    book.save()

    return borrow_record