from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    path('', views.ExpenseListView.as_view(), name='list'),
    path('create/', views.ExpenseCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.ExpenseDetailView.as_view(), name='detail'),
    path('<uuid:pk>/update/', views.ExpenseUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.ExpenseDeleteView.as_view(), name='delete'),
]