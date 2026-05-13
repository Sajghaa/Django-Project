from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'channels', views.ChannelViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'videos', views.VideoViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'playlists', views.PlaylistViewSet)
router.register(r'feed', views.FeedViewSet, basename='feed')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
]