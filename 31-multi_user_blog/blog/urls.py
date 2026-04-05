from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Post URLs - SPECIFIC patterns FIRST
    path('post/create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('post/<slug:slug>/bookmark/', views.bookmark_post, name='bookmark_post'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),
    
    # Posts list
    path('posts/', views.post_list, name='post_list'),
    
    # User Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-posts/', views.my_posts, name='my_posts'),
    path('my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
]