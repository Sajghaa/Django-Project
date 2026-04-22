from django.urls import path
from . import views

app_name = 'budget'

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.transaction_add, name='transaction_add'),
    path('transactions/<int:pk>/edit/', views.transaction_edit, name='transaction_edit'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name='transaction_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Budgets
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/<int:pk>/edit/', views.budget_edit, name='budget_edit'),
    
    # Savings Goals
    path('goals/', views.goals_list, name='goals_list'),
    path('goals/<int:pk>/add-funds/', views.goal_add_funds, name='goal_add_funds'),
    path('goals/<int:pk>/delete/', views.goal_delete, name='goal_delete'),
    
    # Reports
    path('reports/', views.reports, name='reports'),
]