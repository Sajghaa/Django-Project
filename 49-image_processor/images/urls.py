from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'images', views.ImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
]