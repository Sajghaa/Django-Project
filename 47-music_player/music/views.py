from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from django.db.models import Q, Count, Sum
from django.shortcuts import get_object_or_404
from .models import Genre, Artist, Album, Song, Playlist, PlaylistSong, UserFavorite, ListeningHistory, ArtistFollow
from .serializers import (
    UserSerializer, RegisterSerializer, GenreSerializer, ArtistSerializer,
    AlbumSerializer, SongListSerializer, SongDetailSerializer, SongCreateUpdateSerializer,
    PlaylistSerializer, PlaylistCreateUpdateSerializer, PlaylistSongSerializer,
    UserFavoriteSerializer, ListeningHistorySerializer
)
from .permissions import IsOwnerOrReadOnly, CanUploadMusic
from .pagination import CustomPagination
from .filters import SongFilter, ArtistFilter, AlbumFilter
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

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for genres"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'song_count']

class ArtistViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for artists"""
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArtistFilter
    search_fields = ['name', 'bio']
    ordering_fields = ['name', 'monthly_listeners', 'followers_count', 'created_at']

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        """Get all songs by this artist"""
        artist = self.get_object()
        songs = Song.objects.filter(artist=artist)
        page = self.paginate_queryset(songs)
        serializer = SongListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['get'])
    def albums(self, request, pk=None):
        """Get all albums by this artist"""
        artist = self.get_object()
        albums = Album.objects.filter(artist=artist)
        page = self.paginate_queryset(albums)
        serializer = AlbumSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        """Follow/unfollow artist"""
        artist = self.get_object()
        follow, created = ArtistFollow.objects.get_or_create(user=request.user, artist=artist)

        if not created:
            follow.delete()
            following = False
            artist.followers_count -= 1
        else:
            following = True
            artist.followers_count += 1

        artist.save()
        return Response({'following': following, 'followers_count': artist.followers_count})

class AlbumViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for albums"""
    queryset = Album.objects.all()
    serializer_class = AlbumSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = AlbumFilter
    search_fields = ['title', 'artist__name']
    ordering_fields = ['title', 'release_date', 'song_count']

    @action(detail=True, methods=['get'])
    def songs(self, request, pk=None):
        """Get all songs in this album"""
        album = self.get_object()
        songs = Song.objects.filter(album=album)
        page = self.paginate_queryset(songs)
        serializer = SongListSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

class SongViewSet(viewsets.ModelViewSet):
    """ViewSet for songs"""
    queryset = Song.objects.none()
    permission_classes = [IsAuthenticatedOrReadOnly, CanUploadMusic]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SongFilter
    search_fields = ['title', 'artist__name', 'album__title']
    ordering_fields = ['play_count', 'likes_count', 'created_at', 'duration', 'release_date']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Song.objects.none()
        return Song.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return SongListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SongCreateUpdateSerializer
        return SongDetailSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def play(self, request, pk=None):
        """Increment play count and record in history"""
        song = self.get_object()
        song.play_count += 1
        song.save()

        # Record listening history
        if request.user.is_authenticated:
            ListeningHistory.objects.create(
                user=request.user,
                song=song,
                progress=request.data.get('progress', 0)
            )

        return Response({'play_count': song.play_count})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        """Like/unlike song"""
        song = self.get_object()
        like, created = UserFavorite.objects.get_or_create(user=request.user, song=song)

        if not created:
            like.delete()
            liked = False
            song.likes_count -= 1
        else:
            liked = True
            song.likes_count += 1

        song.save()
        return Response({'liked': liked, 'likes_count': song.likes_count})

    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured songs"""
        songs = Song.objects.filter(is_featured=True)[:10]
        serializer = SongListSerializer(songs, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get most played songs"""
        songs = Song.objects.order_by('-play_count')[:20]
        serializer = SongListSerializer(songs, many=True, context={'request': request})
        return Response(serializer.data)

class PlaylistViewSet(viewsets.ModelViewSet):
    """ViewSet for playlists"""
    queryset = Playlist.objects.none()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CustomPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'song_count']
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Playlist.objects.none()
        # Show user's own playlists and public playlists
        return Playlist.objects.filter(Q(user=self.request.user) | Q(is_public=True))

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PlaylistCreateUpdateSerializer
        return PlaylistSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_song(self, request, pk=None):
        """Add song to playlist"""
        playlist = self.get_object()
        song_id = request.data.get('song_id')
        song = get_object_or_404(Song, id=song_id)

        # Check if song already in playlist
        if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
            return Response({'error': 'Song already in playlist'}, status=status.HTTP_400_BAD_REQUEST)

        # Get max order position
        max_order = playlist.playlistsong_set.aggregate(max_order=models.Max('order_position'))['max_order'] or 0

        playlist_song = PlaylistSong.objects.create(
            playlist=playlist,
            song=song,
            order_position=max_order + 1
        )

        # Update playlist stats
        playlist.song_count = playlist.playlistsong_set.count()
        playlist.total_duration = playlist.playlistsong_set.aggregate(
            total=models.Sum('song__duration')
        )['total'] or 0
        playlist.save()

        serializer = PlaylistSongSerializer(playlist_song)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def remove_song(self, request, pk=None):
        """Remove song from playlist"""
        playlist = self.get_object()
        song_id = request.data.get('song_id')
        song = get_object_or_404(Song, id=song_id)

        PlaylistSong.objects.filter(playlist=playlist, song=song).delete()

        # Update playlist stats
        playlist.song_count = playlist.playlistsong_set.count()
        playlist.total_duration = playlist.playlistsong_set.aggregate(
            total=models.Sum('song__duration')
        )['total'] or 0
        playlist.save()

        return Response({'status': 'removed'})

    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder songs in playlist"""
        playlist = self.get_object()
        order_data = request.data.get('order', [])

        for item in order_data:
            PlaylistSong.objects.filter(id=item['id'], playlist=playlist).update(order_position=item['position'])

        return Response({'status': 'reordered'})

class UserLibraryViewSet(viewsets.GenericViewSet):
    """ViewSet for user's music library"""
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    @action(detail=False, methods=['get'])
    def favorites(self, request):
        """Get user's liked songs"""
        favorites = UserFavorite.objects.filter(user=request.user)
        page = self.paginate_queryset(favorites)
        serializer = UserFavoriteSerializer(page, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def recently_played(self, request):
        """Get user's recently played songs"""
        history = ListeningHistory.objects.filter(user=request.user)[:50]
        serializer = ListeningHistorySerializer(history, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """Get personalized song recommendations"""
        # Simple recommendation based on liked songs' genres
        liked_genres = UserFavorite.objects.filter(
            user=request.user
        ).values_list('song__genre', flat=True).distinct()

        if liked_genres:
            recommendations = Song.objects.filter(
                genre__in=liked_genres,
                is_featured=True
            ).exclude(
                id__in=UserFavorite.objects.filter(user=request.user).values_list('song_id', flat=True)
            ).order_by('-play_count')[:20]
        else:
            recommendations = Song.objects.filter(is_featured=True).order_by('-play_count')[:20]

        serializer = SongListSerializer(recommendations, many=True, context={'request': request})
        return Response(serializer.data)

class SearchView(generics.ListAPIView):
    """Global search endpoint"""
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        search_type = self.request.query_params.get('type', 'all')

        if search_type == 'songs':
            return Song.objects.filter(
                Q(title__icontains=query) |
                Q(artist__name__icontains=query)
            ).distinct()
        elif search_type == 'artists':
            return Artist.objects.filter(name__icontains=query)
        elif search_type == 'albums':
            return Album.objects.filter(title__icontains=query)
        else:
            return Song.objects.filter(
                Q(title__icontains=query) |
                Q(artist__name__icontains=query) |
                Q(album__title__icontains=query)
            ).distinct()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        search_type = request.query_params.get('type', 'all')
        if search_type == 'artists':
            serializer = ArtistSerializer(page, many=True, context={'request': request})
        elif search_type == 'albums':
            serializer = AlbumSerializer(page, many=True, context={'request': request})
        else:
            serializer = SongListSerializer(page, many=True, context={'request': request})

        return self.get_paginated_response(serializer.data)