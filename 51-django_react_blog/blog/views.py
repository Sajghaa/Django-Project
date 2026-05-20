from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import Category, Tag, Post, Comment, Like
from .serializers import (
    UserSerializer, RegisterSerializer, CategorySerializer, TagSerializer,
    PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer,
    CommentSerializer
)
from .pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status']
    search_fields = ['title', 'content', 'excerpt', 'author__username']
    ordering_fields = ['created_at', 'published_at', 'views', 'likes']
    ordering = ['-published_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return Post.objects.all()
        return Post.objects.filter(status='published')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        return PostDetailSerializer
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """Like or unlike a post"""
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            like.delete()
            liked = False
            post.likes -= 1
        else:
            liked = True
            post.likes += 1
        
        post.save()
        
        return Response({'liked': liked, 'likes_count': post.likes})
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, pk=None):
        """Increment view count"""
        post = self.get_object()
        post.views += 1
        post.save()
        return Response({'views': post.views})
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured posts"""
        posts = Post.objects.filter(status='published')[:5]
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most viewed posts"""
        posts = Post.objects.filter(status='published').order_by('-views')[:5]
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get most liked posts"""
        posts = Post.objects.filter(status='published').order_by('-likes')[:5]
        serializer = PostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Add comment to post"""
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(post=post, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get post comments"""
        post = self.get_object()
        comments = post.comments.filter(approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get posts by category slug"""
        category_slug = request.query_params.get('slug')
        if category_slug:
            posts = Post.objects.filter(category__slug=category_slug, status='published')
            serializer = PostListSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data)
        return Response({'error': 'Category slug required'}, status=400)
    
    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        """Get posts by tag slug"""
        tag_slug = request.query_params.get('slug')
        if tag_slug:
            posts = Post.objects.filter(tags__slug=tag_slug, status='published')
            serializer = PostListSerializer(posts, many=True, context={'request': request})
            return Response(serializer.data)
        return Response({'error': 'Tag slug required'}, status=400)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        return Comment.objects.filter(approved=True)
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['delete'])
    def delete_comment(self, request, pk=None):
        comment = self.get_object()
        if comment.author == request.user or request.user.is_staff:
            comment.delete()
            return Response({'message': 'Comment deleted'})
        return Response({'error': 'Permission denied'}, status=403)