from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'movies'

urlpatterns = [
    # Movie URLs
    path('', views.MovieListView.as_view(), name='movie_list'),
    path('movie/<slug:slug>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('movie/create/', views.MovieCreateView.as_view(), name='movie_create'),
    path('movie/<slug:slug>/edit/', views.MovieUpdateView.as_view(), name='movie_edit'),
    path('movie/<slug:slug>/delete/', views.MovieDeleteView.as_view(), name='movie_delete'),
    
    # Rating URLs
    path('movie/<slug:slug>/rate/', views.add_rating, name='add_rating'),
    path('movie/<slug:slug>/rate/delete/', views.delete_rating, name='delete_rating'),
    
    # New Feature URLs
    path('reviews/', views.recent_reviews, name='recent_reviews'),
    path('stats/', views.stats_dashboard, name='stats_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile_detail'),
    
    # Authentication URLs - Using custom login view
    path('login/', views.custom_login, name='login'),  # Changed to custom login
    path('logout/', auth_views.LogoutView.as_view(next_page='movies:movie_list'), name='logout'),
]