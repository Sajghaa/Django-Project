from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Genre, Artist, Album, Song, Playlist, PlaylistSong, UserFavorite, ListeningHistory, ArtistFollow

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError("Passwords must match")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        return data

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name', 'slug', 'icon', 'song_count']
        read_only_fields = ['id', 'slug', 'song_count']

class ArtistSerializer(serializers.ModelSerializer):
    follower_count = serializers.IntegerField(source='followers.count', read_only=True)
    is_followed = serializers.SerializerMethodField()

    class Meta:
        model = Artist
        fields = ['id', 'name', 'slug', 'bio', 'avatar', 'cover_image', 'genre',
                  'monthly_listeners', 'follower_count', 'songs_count', 'is_followed',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'monthly_listeners', 'follower_count', 'songs_count', 'created_at', 'updated_at']

    def get_is_followed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ArtistFollow.objects.filter(user=request.user, artist=obj).exists()
        return False

class AlbumSerializer(serializers.ModelSerializer):
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    song_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Album
        fields = ['id', 'title', 'slug', 'artist', 'artist_name', 'cover_image',
                  'release_date', 'genre', 'song_count', 'total_duration', 'created_at']
        read_only_fields = ['id', 'slug', 'song_count', 'total_duration', 'created_at']

class SongListSerializer(serializers.ModelSerializer):
    """Serializer for song list view"""
    artist_name = serializers.CharField(source='artist.name', read_only=True)
    artist_slug = serializers.CharField(source='artist.slug', read_only=True)
    album_title = serializers.CharField(source='album.title', read_only=True, allow_null=True)
    duration_formatted = serializers.CharField(source='get_formatted_duration', read_only=True)
    is_liked = serializers.SerializerMethodField()
    cover_art_url = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'slug', 'artist', 'artist_name', 'artist_slug',
                  'album', 'album_title', 'duration', 'duration_formatted', 'cover_art',
                  'cover_art_url', 'play_count', 'likes_count', 'is_liked', 'release_date']
        read_only_fields = ['id', 'slug', 'play_count', 'likes_count', 'duration_formatted']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavorite.objects.filter(user=request.user, song=obj).exists()
        return False

    def get_cover_art_url(self, obj):
        request = self.context.get('request')
        if obj.cover_art and request:
            return request.build_absolute_uri(obj.cover_art.url)
        if obj.album and obj.album.cover_image:
            return request.build_absolute_uri(obj.album.cover_image.url) if request else None
        return None

class SongDetailSerializer(serializers.ModelSerializer):
    """Serializer for song detail view"""
    artist = ArtistSerializer(read_only=True)
    album = AlbumSerializer(read_only=True)
    genre = GenreSerializer(read_only=True)
    duration_formatted = serializers.CharField(source='get_formatted_duration', read_only=True)
    is_liked = serializers.SerializerMethodField()
    audio_url = serializers.SerializerMethodField()
    cover_art_url = serializers.SerializerMethodField()

    class Meta:
        model = Song
        fields = ['id', 'title', 'slug', 'artist', 'album', 'genre', 'duration',
                  'duration_formatted', 'audio_file', 'audio_url', 'cover_art',
                  'cover_art_url', 'lyrics', 'play_count', 'likes_count', 'is_liked',
                  'release_date', 'created_at']
        read_only_fields = ['id', 'slug', 'play_count', 'likes_count', 'duration_formatted', 'created_at']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return UserFavorite.objects.filter(user=request.user, song=obj).exists()
        return False

    def get_audio_url(self, obj):
        request = self.context.get('request')
        if obj.audio_file and request:
            return request.build_absolute_uri(obj.audio_file.url)
        return None

    def get_cover_art_url(self, obj):
        request = self.context.get('request')
        if obj.cover_art and request:
            return request.build_absolute_uri(obj.cover_art.url)
        if obj.album and obj.album.cover_image:
            return request.build_absolute_uri(obj.album.cover_image.url) if request else None
        return None

class SongCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating songs"""
    class Meta:
        model = Song
        fields = ['title', 'artist', 'album', 'genre', 'duration', 'audio_file',
                  'cover_art', 'lyrics', 'release_date']

    def validate_audio_file(self, value):
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.mp3', '.wav', '.ogg', '.m4a']:
            raise serializers.ValidationError("Invalid audio format")
        if value.size > 20 * 1024 * 1024:  # 20MB
            raise serializers.ValidationError("File too large (max 20MB)")
        return value

class PlaylistSerializer(serializers.ModelSerializer):
    songs = SongListSerializer(many=True, read_only=True)
    song_count = serializers.IntegerField(read_only=True)
    created_by = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'slug', 'description', 'cover_image', 'songs',
                  'song_count', 'total_duration', 'is_public', 'created_by',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'song_count', 'total_duration', 'created_at', 'updated_at']

class PlaylistCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'cover_image', 'is_public']

class PlaylistSongSerializer(serializers.ModelSerializer):
    song = SongListSerializer(read_only=True)

    class Meta:
        model = PlaylistSong
        fields = ['id', 'song', 'order_position', 'added_at']
        read_only_fields = ['id', 'added_at']

class UserFavoriteSerializer(serializers.ModelSerializer):
    song = SongListSerializer(read_only=True)

    class Meta:
        model = UserFavorite
        fields = ['id', 'song', 'created_at']
        read_only_fields = ['id', 'created_at']

class ListeningHistorySerializer(serializers.ModelSerializer):
    song = SongListSerializer(read_only=True)

    class Meta:
        model = ListeningHistory
        fields = ['id', 'song', 'progress', 'played_at']
        read_only_fields = ['id', 'played_at']