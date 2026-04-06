from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    # Comment CRUD
    path('add/<str:app_label>/<str:model_name>/<int:object_id>/', views.add_comment, name='add_comment'),
    path('edit/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('reply/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('<int:comment_id>/', views.comment_detail, name='comment_detail'),
    
    # Interactions
    path('like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('report/<int:comment_id>/', views.report_comment, name='report_comment'),
    
    # Subscriptions
    path('subscribe/<str:app_label>/<str:model_name>/<int:object_id>/', views.subscribe_to_thread, name='subscribe_thread'),
    
    # Moderation
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderate/<int:comment_id>/<str:action>/', views.moderate_comment, name='moderate_comment'),
]