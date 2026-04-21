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
    path('post/create/', views.post_create, name='post_create'),  # ← MUST come BEFORE slug pattern
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/like/', views.like_post, name='like_post'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),  # ← Generic pattern LAST
    
    # Posts list
    path('posts/', views.post_list, name='post_list'),
    
    # Categories & Tags
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    path('author/<str:username>/', views.author_posts, name='author_posts'),
    
    # Search
    path('search/', views.search_results, name='search'),
    
    # Author Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-posts/', views.my_posts, name='my_posts'),
]