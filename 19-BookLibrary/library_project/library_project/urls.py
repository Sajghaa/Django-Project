from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.books.urls")),  # book list
    path("borrows/", include("apps.borrows.urls")),
    path("", include("apps.core.urls")),  # dashboard

    # Add login/logout views
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]

