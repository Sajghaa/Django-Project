from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Home and Auth
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Chat
    path('index/', views.index, name='index'),
    path('room/<slug:slug>/', views.room_detail, name='room'),
    path('create-room/', views.create_room, name='create_room'),
    path('rooms/', views.room_list, name='room_list'),
    path('join/<slug:slug>/', views.join_room, name='join_room'),
    path('leave/<slug:slug>/', views.leave_room, name='leave_room'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
]