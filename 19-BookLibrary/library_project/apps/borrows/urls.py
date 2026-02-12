from django.urls import path
from . import views

urlpatterns = [
    path("borrow/<int:book_id>/", views.borrow_book_view, name="borrow_book"),
    path("return/<int:book_id>/", views.return_book_view, name="return_book"),
]