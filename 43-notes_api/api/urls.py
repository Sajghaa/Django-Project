from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'notebooks', views.NotebookViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'notes', views.NoteViewSet)

urlpatterns = [
    # API root
    path('', include(router.urls)),
    
    # Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomAuthToken.as_view(), name='login'),
    path('auth/token/', obtain_auth_token, name='api_token_auth'),
    
    # Public share
    path('shares/<str:share_token>/', views.PublicNoteView.as_view(), name='public_note'),
    
    # Search
    path('search/', views.SearchView.as_view(), name='search'),
]