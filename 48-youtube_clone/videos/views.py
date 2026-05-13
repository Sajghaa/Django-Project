from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from .models import Channel, Category, Video, Comment, VideoLike, Subscription, Playlist, PlaylistVideo, WatchHistory
from .serializers import (
    UserSerializer, RegisterSerializer, ChannelSerializer, CategorySerializer,
    VideoListSerializer, VideoDetailSerializer, VideoCreateUpdateSerializer,
    CommentSerializer, CommentCreateSerializer, PlaylistSerializer, PlaylistCreateUpdateSerializer
)
from .permissions import IsChannelOwner, CanComment, CanSubscribe
from .pagination import CustomPagination
from .filters import VideoFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
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
        
        # Create default channel for user
        Channel.objects.create(
            user=user,
            name=f"{user.username}'s Channel"
        )
        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    """Custom auth token endpoint"""
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username
        })

class ChannelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for channels"""
    queryset = Channel.objects.all()
    serializer_class = ChannelSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'subscribers', 'created_at']
    ordering = ['-subscribers']
    
    @action(detail=True, methods=['get'])
    def videos(self, request, pk=None):
        """Get all videos from this channel"""
        channel = self.get_object()
        videos = Video.objects.filter(channel=channel, privacy='public')
        page = self.paginate_queryset(videos)
        serializer = VideoListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, pk=None):
        """Subscribe/Unsubscribe to channel"""
        channel = self.get_object()
        
        if channel.user == request.user:
            return Response({'error': 'Cannot subscribe to your own channel'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        subscription, created = Subscription.objects.get_or_create(
            subscriber=request.user,
            channel=channel
        )
        
        if not created:
            subscription.delete()
            subscribed = False
            channel.subscribers -= 1
        else:
            subscribed = True
            channel.subscribers += 1
        
        channel.save()
        
        return Response({
            'subscribed': subscribed,
            'subscribers_count': channel.subscribers
        })

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination

class VideoViewSet(viewsets.ModelViewSet):
    """ViewSet for videos"""
    queryset = Video.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly, IsChannelOwner]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = VideoFilter
    search_fields = ['title', 'description', 'tags', 'channel__name']
    ordering_fields = ['views', 'likes', 'published_at', 'duration']
    ordering = ['-published_at']
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Video.objects.none()
        
        # For unauthenticated users, show only public videos
        if not self.request.user.is_authenticated:
            return Video.objects.filter(privacy='public')
        
        # For authenticated users, show public videos + their own private videos
        user_channels = Channel.objects.filter(user=self.request.user)
        return Video.objects.filter(
            Q(privacy='public') | Q(channel__in=user_channels)
        )
    
    def get_serializer_class(self):
        if self.action == 'list':
            return VideoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return VideoCreateUpdateSerializer
        return VideoDetailSerializer
    
    def perform_create(self, serializer):
        channel = get_object_or_404(Channel, user=self.request.user)
        serializer.save(channel=channel)
    
    @action(detail=True, methods=['post'])
    def view(self, request, pk=None):
        """Increment view count"""
        video = self.get_object()
        video.views += 1
        video.save()
        return Response({'views': video.views})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like or dislike video"""
        video = self.get_object()
        value = request.data.get('value', 1)  # 1 for like, -1 for dislike
        
        if not video.allow_likes:
            return Response({'error': 'Likes are disabled for this video'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        like, created = VideoLike.objects.get_or_create(
            video=video,
            user=request.user,
            defaults={'value': value}
        )
        
        if not created:
            if like.value == value:
                like.delete()
                liked = False
                if value == 1:
                    video.likes -= 1
                else:
                    video.dislikes -= 1
            else:
                # Update existing like/dislike
                if like.value == 1:
                    video.likes -= 1
                else:
                    video.dislikes -= 1
                
                like.value = value
                like.save()
                
                if value == 1:
                    video.likes += 1
                else:
                    video.dislikes += 1
                
                liked = True
        else:
            liked = True
            if value == 1:
                video.likes += 1
            else:
                video.dislikes += 1
        
        video.save()
        
        return Response({
            'liked': liked if value == 1 else None,
            'disliked': liked if value == -1 else None,
            'likes_count': video.likes,
            'dislikes_count': video.dislikes
        })
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get video comments"""
        video = self.get_object()
        comments = video.comments.filter(parent=None)
        page = self.paginate_queryset(comments)
        serializer = CommentSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanComment])
    def add_comment(self, request, pk=None):
        """Add comment to video"""
        video = self.get_object()
        
        if not video.allow_comments:
            return Response({'error': 'Comments are disabled for this video'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        comment = serializer.save(video=video, user=request.user)
        
        # Update comment count
        video.comments_count = video.comments.count()
        video.save()
        
        return Response(CommentSerializer(comment, context={'request': request}).data, 
                       status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """Get related videos"""
        video = self.get_object()
        # Simple related algorithm: same category or similar tags
        related = Video.objects.filter(
            Q(category=video.category) | Q(tags__icontains=video.tags.split(',')[0] if video.tags else ''),
            privacy='public'
        ).exclude(id=video.id)[:10]
        
        serializer = VideoListSerializer(related, many=True, context={'request': request})
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet for comments"""
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()
        return Comment.objects.filter(user=self.request.user)

class PlaylistViewSet(viewsets.ModelViewSet):
    """ViewSet for playlists"""
    queryset = Playlist.objects.none()
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Playlist.objects.none()
        return Playlist.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PlaylistCreateUpdateSerializer
        return PlaylistSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def add_video(self, request, pk=None):
        """Add video to playlist"""
        playlist = self.get_object()
        video_id = request.data.get('video_id')
        video = get_object_or_404(Video, id=video_id)
        
        if PlaylistVideo.objects.filter(playlist=playlist, video=video).exists():
            return Response({'error': 'Video already in playlist'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Get max order position
        max_order = playlist.videos_info.aggregate(max=models.Max('order_position'))['max_order'] or 0
        
        playlist_video = PlaylistVideo.objects.create(
            playlist=playlist,
            video=video,
            order_position=max_order + 1
        )
        
        playlist.video_count = playlist.videos_info.count()
        playlist.save()
        
        return Response({'message': 'Video added to playlist'})
    
    @action(detail=True, methods=['delete'])
    def remove_video(self, request, pk=None):
        """Remove video from playlist"""
        playlist = self.get_object()
        video_id = request.data.get('video_id')
        video = get_object_or_404(Video, id=video_id)
        
        PlaylistVideo.objects.filter(playlist=playlist, video=video).delete()
        
        playlist.video_count = playlist.videos_info.count()
        playlist.save()
        
        return Response({'message': 'Video removed from playlist'})

class FeedViewSet(viewsets.GenericViewSet):
    """ViewSet for feeds and recommendations"""
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    
    @action(detail=False, methods=['get'])
    def subscriptions(self, request):
        """Get videos from subscribed channels"""
        subscribed_channels = Subscription.objects.filter(
            subscriber=request.user
        ).values_list('channel', flat=True)
        
        videos = Video.objects.filter(
            channel__in=subscribed_channels,
            privacy='public'
        ).order_by('-published_at')
        
        page = self.paginate_queryset(videos)
        serializer = VideoListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def trending(self, request):
        """Get trending videos (based on views and likes)"""
        from django.db.models import F
        videos = Video.objects.filter(privacy='public').annotate(
            score=(F('views') + F('likes') * 10) / (timezone.now() - F('published_at')).days
        ).order_by('-score')[:20]
        
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recommended(self, request):
        """Get personalized recommendations"""
        # Simple recommendation based on watch history
        watched_categories = WatchHistory.objects.filter(
            user=request.user
        ).values_list('video__category', flat=True).distinct()
        
        if watched_categories:
            videos = Video.objects.filter(
                category__in=watched_categories,
                privacy='public'
            ).exclude(
                id__in=WatchHistory.objects.filter(user=request.user).values_list('video_id', flat=True)
            ).order_by('-views')[:20]
        else:
            videos = Video.objects.filter(privacy='public', is_featured=True).order_by('-views')[:20]
        
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get user's watch history"""
        history = WatchHistory.objects.filter(user=request.user).select_related('video')
        page = self.paginate_queryset(history)
        
        videos = [item.video for item in page]
        serializer = VideoListSerializer(videos, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)