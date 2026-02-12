from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.books.models import Book

User = get_user_model()


class BorrowRecord(models.Model):

    class Status(models.TextChoices):
        BORROWED = "BORROWED", "Borrowed"
        RETURNED = "RETURNED", "Returned"
        OVERDUE = "OVERDUE", "Overdue"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="borrow_records"
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="borrow_records"
    )

    borrow_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.BORROWED
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def mark_as_returned(self):
        self.return_date = timezone.now().date()
        self.status = self.Status.RETURNED
        self.save()

    def check_overdue(self):
        if (
            self.status == self.Status.BORROWED
            and self.due_date < timezone.now().date()
        ):
            self.status = self.Status.OVERDUE
            self.save()

    def __str__(self):
        return f"{self.user} borrowed {self.book.title}"