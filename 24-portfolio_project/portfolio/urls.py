from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('contact/', views.contact, name='contact'),
    
    # Portfolio URLs
    path('portfolio/', views.portfolio_list, name='portfolio_list'),
    path('portfolio/<slug:slug>/', views.portfolio_detail, name='portfolio_detail'),
    
    # Blog URLs
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Admin URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/blog/add/', views.add_blog_post, name='add_blog_post'),
    path('admin/blog/<slug:slug>/edit/', views.edit_blog_post, name='edit_blog_post'),
    path('admin/blog/<slug:slug>/delete/', views.delete_blog_post, name='delete_blog_post'),
    path('admin/messages/', views.view_messages, name='view_messages'),
]