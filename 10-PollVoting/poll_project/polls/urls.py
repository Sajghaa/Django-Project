from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('vote/<int:question_id>/', views.vote, name='vote'),
    path('results/<int:question_id>/', views.results, name='results'),
]
