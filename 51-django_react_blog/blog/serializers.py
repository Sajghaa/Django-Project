from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Tag, Post, Comment, Like

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

class CategorySerializer(serializers.ModelSerializer):
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count', 'created_at']
        read_only_fields = ['id', 'slug', 'post_count', 'created_at']
    
    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'slug', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'content', 'approved', 'created_at']
        read_only_fields = ['id', 'author', 'approved', 'created_at']

class PostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_slug = serializers.CharField(source='category.slug', read_only=True)
    tags_list = TagSerializer(many=True, read_only=True, source='tags')
    comment_count = serializers.SerializerMethodField()
    reading_time = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'author_name', 'category', 'category_name',
            'category_slug', 'tags_list', 'excerpt', 'featured_image', 'status',
            'views', 'likes', 'comment_count', 'reading_time', 'created_at', 'published_at'
        ]
        read_only_fields = ['id', 'slug', 'views', 'likes', 'reading_time', 'created_at', 'published_at']
    
    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()

class PostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    category_detail = CategorySerializer(source='category', read_only=True)
    tags_detail = TagSerializer(many=True, read_only=True, source='tags')
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    reading_time = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'author_name', 'author_email',
            'category', 'category_detail', 'tags', 'tags_detail', 'content',
            'excerpt', 'featured_image', 'status', 'views', 'likes', 'comment_count',
            'comments', 'reading_time', 'is_liked', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'views', 'likes', 'reading_time', 'created_at', 'updated_at'
        ]
    
    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    tags_input = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'tags_input', 'content', 'excerpt', 'featured_image', 'status']
    
    def create(self, validated_data):
        tags_input = validated_data.pop('tags_input', '')
        post = Post.objects.create(**validated_data)
        
        if tags_input:
            tag_names = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
        
        return post
    
    def update(self, instance, validated_data):
        tags_input = validated_data.pop('tags_input', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if tags_input is not None:
            instance.tags.clear()
            tag_names = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        
        return instance