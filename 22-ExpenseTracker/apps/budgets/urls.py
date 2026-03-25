from django.urls import path
from . import views

app_name = 'budgets'

urlpatterns = [
    path('', views.BudgetListView.as_view(), name='list'),
    path('create/', views.BudgetCreateView.as_view(), name='create'),
    path('<uuid:pk>/', views.BudgetDetailView.as_view(), name='detail'),
    path('<uuid:pk>/update/', views.BudgetUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.BudgetDeleteView.as_view(), name='delete'),
]