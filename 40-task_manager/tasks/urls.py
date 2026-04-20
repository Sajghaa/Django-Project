from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Tasks
    path('tasks/', views.task_list, name='task_list'),
    path('task/<int:pk>/', views.task_detail, name='task_detail'),
    path('task/create/', views.task_create, name='task_create'),
    path('task/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('task/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('task/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('task/<int:pk>/status/<str:status>/', views.task_status_update, name='task_status_update'),
    
    # Subtasks
    path('subtask/<int:pk>/toggle/', views.subtask_toggle, name='subtask_toggle'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
    
    # Projects
    path('projects/', views.project_list, name='project_list'),
    path('project/<int:pk>/delete/', views.project_delete, name='project_delete'),
    
    # Calendar
    path('calendar/', views.task_calendar, name='calendar'),
]