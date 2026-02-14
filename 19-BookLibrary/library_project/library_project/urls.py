from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("apps.books.urls")),
    path("", include("apps.core.urls")),
    path("borrows/", include("apps.borrows.urls")),
]
