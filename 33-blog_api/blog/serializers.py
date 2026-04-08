from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Tag, Post, Comment

class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'post_count']
        read_only_fields = ['id', 'created_at', 'post_count']
    
    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()

class TagSerializer(serializers.ModelSerializer):
    """Tag serializer"""
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id']

class CommentSerializer(serializers.ModelSerializer):
    """Comment serializer"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'author_name', 'author_email', 'content', 'approved', 'created_at']
        read_only_fields = ['id', 'author', 'author_name', 'author_email', 'created_at', 'approved']

class PostListSerializer(serializers.ModelSerializer):
    """Post list serializer (minimal fields)"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    comment_count = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'author_name', 'category', 'category_name',
            'excerpt', 'featured_image', 'status', 'views', 'likes', 
            'published_at', 'reading_time', 'comment_count', 'tags_list'
        ]
        read_only_fields = ['id', 'views', 'likes', 'reading_time', 'comment_count', 'tags_list']
    
    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()
    
    def get_tags_list(self, obj):
        return [tag.name for tag in obj.tags.all()]

class PostDetailSerializer(serializers.ModelSerializer):
    """Post detail serializer (full fields)"""
    author_name = serializers.CharField(source='author.username', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    tags_list = TagSerializer(many=True, read_only=True, source='tags')
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'author', 'author_name', 'author_email', 'author_bio',
            'category', 'category_name', 'tags', 'tags_list', 'content', 'excerpt',
            'featured_image', 'status', 'views', 'likes', 'created_at', 'updated_at',
            'published_at', 'reading_time', 'comments', 'comment_count'
        ]
        read_only_fields = ['id', 'views', 'likes', 'created_at', 'updated_at', 'reading_time']
    
    def get_comment_count(self, obj):
        return obj.comments.filter(approved=True).count()

class PostCreateUpdateSerializer(serializers.ModelSerializer):
    """Post create/update serializer"""
    tags_input = serializers.CharField(write_only=True, required=False, help_text="Comma-separated tags")
    
    class Meta:
        model = Post
        fields = [
            'title', 'category', 'tags', 'tags_input', 'content', 'excerpt',
            'featured_image', 'status'
        ]
    
    def create(self, validated_data):
        tags_input = validated_data.pop('tags_input', '')
        post = Post.objects.create(**validated_data)
        
        # Process tags
        if tags_input:
            tag_names = [tag.strip().lower() for tag in tags_input.split(',')]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                post.tags.add(tag)
        
        return post
    
    def update(self, instance, validated_data):
        tags_input = validated_data.pop('tags_input', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags_input is not None:
            instance.tags.clear()
            tag_names = [tag.strip().lower() for tag in tags_input.split(',')]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                instance.tags.add(tag)
        
        return instance