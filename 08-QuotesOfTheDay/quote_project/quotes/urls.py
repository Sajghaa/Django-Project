from django.urls import path
from . import views

urlpatterns = [
    path('', views.quote_view, name='quote'),
]
