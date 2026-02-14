from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.borrows.models import BorrowRecord
from .models import Book


def book_list(request):
    books = Book.objects.all()
     
    borrowed_book_ids = BorrowRecord.objects.filter(
        user=request.user,
        status=BorrowRecord.Status.BORROWED
    ).values_list("book_id", flat=True)

    return render(
        request, 
        
        "books/book_list.html", 
        {
            "books": books,
            "borrowed_book_ids":borrowed_book_ids,
         },
         )