from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Notebook, Tag, Note, Attachment, NoteShare, NoteVersion

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class NotebookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notebook
        fields = ['id', 'name', 'description', 'color', 'icon', 'note_count', 'is_default', 'created_at', 'updated_at']
        read_only_fields = ['id', 'note_count', 'created_at', 'updated_at']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'note_count', 'created_at']
        read_only_fields = ['id', 'note_count', 'created_at']

class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Attachment
        fields = ['id', 'filename', 'file_size', 'file_type', 'file_url', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None

class NoteListSerializer(serializers.ModelSerializer):
    """Serializer for list view (minimal fields)"""
    notebook_name = serializers.CharField(source='notebook.name', read_only=True)
    tag_names = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'summary', 'color', 'notebook', 'notebook_name',
            'tag_names', 'is_favorite', 'is_archived', 'pinned', 'view_count',
            'updated_at', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'summary', 'view_count', 'updated_at', 'created_at']
    
    def get_tag_names(self, obj):
        return [tag.name for tag in obj.tags.all()]

class NoteDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view (full fields)"""
    notebook_detail = NotebookSerializer(source='notebook', read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    share_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'content', 'content_html', 'summary', 'color',
            'notebook', 'notebook_detail', 'tags', 'tags_detail', 'attachments',
            'is_favorite', 'is_archived', 'is_trash', 'pinned', 'order_position',
            'view_count', 'reminder_date', 'share_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'content_html', 'summary', 'view_count', 'created_at', 'updated_at']
    
    def get_share_url(self, obj):
        if hasattr(obj, 'share') and obj.share:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(f"/api/shares/{obj.share.share_token}/")
        return None

class NoteCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create/update operations"""
    tags_input = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = Note
        fields = [
            'title', 'content', 'notebook', 'tags', 'tags_input', 'color',
            'is_favorite', 'is_archived', 'reminder_date', 'pinned'
        ]
    
    def create(self, validated_data):
        tags_input = validated_data.pop('tags_input', '')
        note = Note.objects.create(**validated_data)
        
        # Process tags
        if tags_input:
            tag_names = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    user=note.user,
                    name=tag_name
                )
                note.tags.add(tag)
        
        return note
    
    def update(self, instance, validated_data):
        tags_input = validated_data.pop('tags_input', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update tags if provided
        if tags_input is not None:
            instance.tags.clear()
            tag_names = [tag.strip().lower() for tag in tags_input.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(
                    user=instance.user,
                    name=tag_name
                )
                instance.tags.add(tag)
        
        return instance

class NoteShareSerializer(serializers.ModelSerializer):
    share_url = serializers.SerializerMethodField()
    
    class Meta:
        model = NoteShare
        fields = ['share_token', 'share_password', 'expires_at', 'view_count', 'share_url', 'created_at']
        read_only_fields = ['share_token', 'view_count', 'created_at']
        extra_kwargs = {
            'share_password': {'write_only': True, 'required': False},
            'expires_at': {'required': False}
        }
    
    def get_share_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f"/api/shares/{obj.share_token}/")
        return None
    
# Add this to api/serializers.py if missing
class NoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersion
        fields = ['id', 'title', 'content', 'version_number', 'created_at']
        read_only_fields = ['id', 'version_number', 'created_at']