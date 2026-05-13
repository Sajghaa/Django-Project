from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Channel, Category, Video, Comment, VideoLike, Subscription, Playlist, PlaylistVideo, WatchHistory

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

class ChannelSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    is_subscribed = serializers.SerializerMethodField()
    subscriber_count = serializers.IntegerField(source='subscribers', read_only=True)

    class Meta:
        model = Channel
        fields = ['id', 'user', 'user_details', 'name', 'slug', 'description', 
                  'avatar', 'banner', 'subscriber_count', 'total_views', 
                  'is_subscribed', 'created_at']
        read_only_fields = ['id', 'slug', 'subscribers', 'total_views', 'created_at']

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(subscriber=request.user, channel=obj).exists()
        return False

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'icon']

class VideoListSerializer(serializers.ModelSerializer):
    """Serializer for video list view"""
    channel_name = serializers.CharField(source='channel.name', read_only=True)
    channel_avatar = serializers.ImageField(source='channel.avatar', read_only=True)
    channel_slug = serializers.CharField(source='channel.slug', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    duration_formatted = serializers.CharField(source='get_formatted_duration', read_only=True)
    thumbnail_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'slug', 'channel', 'channel_name', 'channel_avatar', 
                  'channel_slug', 'category', 'category_name', 'thumbnail', 'thumbnail_url',
                  'duration', 'duration_formatted', 'views', 'likes', 'comments_count',
                  'is_liked', 'created_at', 'published_at']
        read_only_fields = ['id', 'slug', 'views', 'likes', 'comments_count', 'created_at']

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            like = VideoLike.objects.filter(video=obj, user=request.user).first()
            return like.value == 1 if like else None
        return None

class VideoDetailSerializer(serializers.ModelSerializer):
    """Serializer for video detail view"""
    channel = ChannelSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    duration_formatted = serializers.CharField(source='get_formatted_duration', read_only=True)
    video_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    user_like = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'title', 'slug', 'channel', 'category', 'description',
                  'video_file', 'video_url', 'thumbnail', 'thumbnail_url', 'duration',
                  'duration_formatted', 'views', 'likes', 'dislikes', 'comments_count',
                  'privacy', 'allow_comments', 'allow_likes', 'tags', 'user_like',
                  'created_at', 'published_at']
        read_only_fields = ['id', 'slug', 'views', 'likes', 'dislikes', 'comments_count', 'created_at']

    def get_video_url(self, obj):
        request = self.context.get('request')
        if obj.video_file and request:
            return request.build_absolute_uri(obj.video_file.url)
        return None

    def get_thumbnail_url(self, obj):
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None

    def get_user_like(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            like = VideoLike.objects.filter(video=obj, user=request.user).first()
            return like.value if like else 0
        return 0

class VideoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating videos"""
    class Meta:
        model = Video
        fields = ['title', 'category', 'description', 'video_file', 'thumbnail',
                  'privacy', 'allow_comments', 'allow_likes', 'tags']

    def validate_video_file(self, value):
        import os
        ext = os.path.splitext(value.name)[1].lower()
        if ext not in ['.mp4', '.mov', '.avi', '.webm']:
            raise serializers.ValidationError("Invalid video format")
        if value.size > 500 * 1024 * 1024:  # 500MB
            raise serializers.ValidationError("Video too large (max 500MB)")
        return value

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_avatar = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'user_avatar', 'content', 'likes',
                  'is_pinned', 'replies', 'is_liked', 'created_at']
        read_only_fields = ['id', 'user', 'likes', 'created_at']

    def get_user_avatar(self, obj):
        if hasattr(obj.user, 'channel') and obj.user.channel.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.channel.avatar.url)
        return None

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_is_liked(self, obj):
        # For comment likes (to be implemented)
        return False

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'parent']

class PlaylistSerializer(serializers.ModelSerializer):
    video_count = serializers.IntegerField(read_only=True)
    videos = VideoListSerializer(many=True, read_only=True)

    class Meta:
        model = Playlist
        fields = ['id', 'name', 'slug', 'description', 'is_public', 
                  'video_count', 'videos', 'created_at']
        read_only_fields = ['id', 'slug', 'video_count', 'created_at']

class PlaylistCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Playlist
        fields = ['name', 'description', 'is_public']