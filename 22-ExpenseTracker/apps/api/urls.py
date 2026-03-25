from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'expenses', views.ExpenseViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'budgets', views.BudgetViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]