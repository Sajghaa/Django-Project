from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'agents', views.AgentViewSet)
router.register(r'property-types', views.PropertyTypeViewSet)
router.register(r'features', views.PropertyFeatureViewSet)
router.register(r'properties', views.PropertyViewSet)
router.register(r'images', views.PropertyImageViewSet)
router.register(r'inquiries', views.InquiryViewSet)
router.register(r'saved-properties', views.SavedPropertyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
]