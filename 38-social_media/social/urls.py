from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    # Home & Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Feed
    path('feed/', views.feed, name='feed'),
    path('explore/', views.explore, name='explore'),
    
    # Profile
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers'),
    path('profile/<str:username>/following/', views.following_list, name='following'),
    
    # Posts
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', views.like_post, name='like_post'),
    
    # Interactions
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
]