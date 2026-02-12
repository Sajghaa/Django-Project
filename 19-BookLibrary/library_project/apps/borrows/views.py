from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError

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