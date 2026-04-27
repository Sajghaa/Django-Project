from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'categories', views.JobCategoryViewSet)
router.register(r'skills', views.JobSkillViewSet)
router.register(r'jobs', views.JobViewSet)
router.register(r'applications', views.JobApplicationViewSet)
router.register(r'saved-jobs', views.SavedJobViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
]