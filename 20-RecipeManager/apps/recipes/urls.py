from django.urls import path
from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.recipe_list, name='list'),
    path('recipe/<int:pk>/', views.recipe_detail, name='detail'),
    path('recipe/create/', views.recipe_create, name='create'),
    path('recipe/<int:pk>/update/', views.recipe_update, name='update'),
    path('recipe/<int:pk>/delete/', views.recipe_delete, name='delete'),
]