from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.books.models import Book
from .models import BorrowRecord


MAX_BORROWED_BOOKS = 3  # max books a user can borrow at a time


@transaction.atomic
def borrow_book(user, book_id, days=14):
    # ... existing borrow_book logic ...


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