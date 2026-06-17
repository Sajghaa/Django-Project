from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'customers', views.CustomerViewSet)
router.register(r'interactions', views.InteractionViewSet)
router.register(r'leads', views.LeadViewSet)
router.register(r'opportunities', views.OpportunityViewSet)
router.register(r'register', views.RegisterViewSet, basename='register')
router.register(r'login', views.LoginViewSet, basename='login')

urlpatterns = [
    path('', include(router.urls)),
]