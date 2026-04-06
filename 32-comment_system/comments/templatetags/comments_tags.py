from django import template
from django.contrib.contenttypes.models import ContentType
from comments.forms import CommentForm, CommentReplyForm
from comments.models import Comment

register = template.Library()

@register.inclusion_tag('comments/comment_list.html', takes_context=True)
def render_comments(context, obj):
    """
    Render all comments for an object
    Usage: {% render_comments post %}
    """
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(
        content_type=content_type,
        object_id=obj.id,
        status='approved',
        parent=None
    ).select_related('author').prefetch_related('replies')
    
    return {
        'comments': comments,
        'app_label': content_type.app_label,
        'model_name': content_type.model,
        'object_id': obj.id,
        'object': obj,
        'user': context['request'].user,
        'comment_form': CommentForm(),
        'reply_form': CommentReplyForm(),
    }

@register.inclusion_tag('comments/comment_count.html')
def comment_count(obj):
    """
    Display comment count for an object
    Usage: {% comment_count post %}
    """
    content_type = ContentType.objects.get_for_model(obj)
    count = Comment.objects.filter(
        content_type=content_type,
        object_id=obj.id,
        status='approved'
    ).count()
    
    return {'count': count}

@register.simple_tag
def get_comment_count(obj):
    """Get comment count as integer"""
    content_type = ContentType.objects.get_for_model(obj)
    return Comment.objects.filter(
        content_type=content_type,
        object_id=obj.id,
        status='approved'
    ).count()