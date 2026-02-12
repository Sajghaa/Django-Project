from django.contrib import admin
from .models import BorrowRecord

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "book",
        "borrow_date",
        "due_date",
        "status",
    )
    list_filter = ("status",)
