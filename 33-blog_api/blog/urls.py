from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'posts', views.PostViewSet)
router.register(r'comments', views.CommentViewSet)

urlpatterns = [
    # API root
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]