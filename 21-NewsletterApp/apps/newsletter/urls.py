from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # Public URLs
    path('subscribe/', views.subscribe, name='subscribe'),
    path('subscribe/success/', views.subscribe_success, name='subscribe_success'),
    path('confirm/<uuid:token>/', views.confirm_subscription, name='confirm'),
    path('unsubscribe/', views.unsubscribe, name='unsubscribe'),
    path('unsubscribe/<uuid:token>/', views.unsubscribe, name='unsubscribe_token'),
    
    # Admin URLs
    path('admin/newsletters/', views.newsletter_list, name='newsletter_list'),
    path('admin/newsletters/create/', views.newsletter_create, name='newsletter_create'),
    path('admin/newsletters/<int:pk>/edit/', views.newsletter_edit, name='newsletter_edit'),
    path('admin/newsletters/<int:pk>/delete/', views.newsletter_delete, name='newsletter_delete'),
    path('admin/newsletters/<int:pk>/send/', views.newsletter_send, name='newsletter_send'),
]