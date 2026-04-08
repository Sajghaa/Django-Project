from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from .models import Category, Tag, Post, Comment
from .serializers import (
    UserSerializer, CategorySerializer, TagSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer
)
from .permissions import IsAuthorOrReadOnly, IsAdminOrReadOnly, IsCommentAuthorOrReadOnly
from .pagination import CustomPagination, PostPagination, CommentPagination
from .filters import PostFilter, CategoryFilter

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing users"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['date_joined', 'username']
    ordering = ['date_joined']

class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    pagination_class = CustomPagination

class TagViewSet(viewsets.ModelViewSet):
    """ViewSet for tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']
    pagination_class = CustomPagination

class PostViewSet(viewsets.ModelViewSet):
    """ViewSet for posts"""
    queryset = Post.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['published_at', 'created_at', 'views', 'likes', 'title']
    ordering = ['-published_at']
    pagination_class = PostPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def get_queryset(self):
        """Filter posts based on user role"""
        user = self.request.user
        queryset = Post.objects.all()
        
        # Non-admin users only see published posts
        if not user.is_staff:
            queryset = queryset.filter(status='published')
        
        return queryset
    
    def perform_create(self, serializer):
        """Set author when creating post"""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a post"""
        post = self.get_object()
        user = request.user
        
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        post.likes += 1
        post.save()
        
        return Response({
            'likes': post.likes,
            'message': 'Post liked successfully'
        })
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        post = self.get_object()
        post.views += 1
        post.save()
        
        return Response({'views': post.views})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts"""
        featured_posts = Post.objects.filter(status='published')[:5]
        serializer = self.get_serializer(featured_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most viewed posts"""
        popular_posts = Post.objects.filter(status='published').order_by('-views')[:5]
        serializer = self.get_serializer(popular_posts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get most liked posts"""
        trending_posts = Post.objects.filter(status='published').order_by('-likes')[:5]
        serializer = self.get_serializer(trending_posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments"""
    queryset = Comment.objects.all()  # ADD THIS LINE - missing queryset
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'approved']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    pagination_class = CommentPagination
    
    def get_queryset(self):
        """Filter comments based on user role"""
        queryset = Comment.objects.filter(approved=True)
        
        # If user is admin, show all comments
        if self.request.user.is_staff:
            queryset = Comment.objects.all()
        
        # Filter by post if provided
        post_id = self.request.query_params.get('post')
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """Set author when creating comment"""
        serializer.save(author=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_comments(self, request):
        """Get current user's comments"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        comments = Comment.objects.filter(author=request.user)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)