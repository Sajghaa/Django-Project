from django.urls import path
from . import views

app_name = 'categories'

urlpatterns = [
    path('', views.CategoryListView.as_view(), name='list'),
    path('create/', views.CategoryCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.CategoryDetailView.as_view(), name='detail'),
    path('<uuid:pk>/update/', views.CategoryUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.CategoryDeleteView.as_view(), name='delete'),
]