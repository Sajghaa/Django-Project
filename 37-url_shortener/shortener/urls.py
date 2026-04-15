from django.urls import path
from . import views

app_name = 'shortener'

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # URL Management
    path('create/', views.create_short_url, name='create'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('stats/<str:short_code>/', views.url_stats, name='url_stats'),
    path('edit/<str:short_code>/', views.edit_url, name='edit_url'),
    path('delete/<str:short_code>/', views.delete_url, name='delete_url'),
    
    # Redirect
    path('<str:short_code>/', views.redirect_to_url, name='redirect'),
]