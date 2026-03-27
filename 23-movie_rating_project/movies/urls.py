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
    
    # Authentication URLs (simple built-in views)
    path('login/', auth_views.LoginView.as_view(template_name='movies/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]