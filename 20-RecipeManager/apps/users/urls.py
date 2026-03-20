# apps/recipes/urls.py
from django.urls import path
from . import views

app_name = 'apps.users'

urlpatterns = [
    # Add your URL patterns here
    #path('', views.index, name='index'),
    # You can add more patterns like:
    # path('<int:pk>/', views.detail, name='detail'),
    # path('create/', views.create, name='create'),
]