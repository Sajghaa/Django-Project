from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<int:year>/<int:month>/<int:day>/<slug:slug>/', 
         views.PostDetailView.as_view(), name='post_detail'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    path('category/<slug:slug>/', views.CategoryPostsView.as_view(), name='category_posts'),
    path('search/', views.SearchResultsView.as_view(), name='search'),
    path('drafts/', views.DraftListView.as_view(), name='draft_list'),
]