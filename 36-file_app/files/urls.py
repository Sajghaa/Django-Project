from django.urls import path
from . import views

app_name = 'files'

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # File Management
    path('upload/', views.upload_file, name='upload'),
    path('my-files/', views.my_files, name='my_files'),
    path('shared-with-me/', views.shared_with_me, name='shared_with_me'),
    path('file/<int:file_id>/', views.file_detail, name='file_detail'),
    path('file/<int:file_id>/share/', views.share_file, name='share_file'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('download/<int:file_id>/', views.download_file, name='download'),
    path('s/<str:access_code>/', views.public_download, name='public_download'),
    path('public-files/', views.file_list, name='file_list'),  # For public file listing
    path('profile/', views.profile, name='profile'), 
]