from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Post CRUD - SPECIFIC paths MUST come BEFORE the generic slug pattern
    path('post/create/', views.post_create, name='post_create'),
    path('post/<slug:slug>/edit/', views.post_edit, name='post_edit'),
    path('post/<slug:slug>/delete/', views.post_delete, name='post_delete'),
    path('post/<slug:slug>/like/', views.like_toggle, name='like_toggle'),
    path('post/<slug:slug>/', views.post_detail, name='post_detail'),  # Generic LAST
    
    # Comments
    path('comment/<int:comment_id>/like/', views.comment_like_toggle, name='comment_like_toggle'),
    
    # Search
    path('search/', views.search, name='search'),
    
    # Categories & Tags
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.tag_posts, name='tag_posts'),
    
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Profile
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
]