from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('students/', views.student_list, name='student_list'),
    path('students/create/', views.student_create, name='student_create'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('students/<int:pk>/edit/', views.student_update, name='student_update'),
    path('students/<int:pk>/delete/', views.student_delete, name='student_delete'),
    
    path('departments/', views.department_list, name='department_list'),
    path('courses/', views.course_list, name='course_list'),
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('results/', views.result_list, name='result_list'),
]