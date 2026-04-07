from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import Comment, CommentLike, CommentReport, CommentSubscription
from .forms import CommentForm, CommentReplyForm, CommentReportForm, CommentSearchForm

def is_moderator(user):
    return user.is_authenticated and (user.is_superuser or user.has_perm('comments.can_moderate_comments'))

def get_comments_for_object(request, content_type, object_id, template='comments/comment_list.html'):
    """Generic function to get comments for any model"""
    content_type_obj = ContentType.objects.get(app_label=content_type, model=content_type)
    obj = content_type_obj.get_object_for_this_type(id=object_id)
    
    # Get approved comments
    comments = Comment.objects.filter(
        content_type=content_type_obj,
        object_id=object_id,
        status='approved',
        parent=None
    ).select_related('author').prefetch_related('replies')
    
    # Get comment count
    comment_count = comments.count()
    
    # Check if user is subscribed
    is_subscribed = False
    if request.user.is_authenticated:
        is_subscribed = CommentSubscription.objects.filter(
            user=request.user,
            content_type=content_type_obj,
            object_id=object_id
        ).exists()
    
    context = {
        'comments': comments,
        'comment_count': comment_count,
        'content_type': content_type,
        'object_id': object_id,
        'object': obj,
        'is_subscribed': is_subscribed,
        'comment_form': CommentForm(),
        'reply_form': CommentReplyForm(),
    }
    
    return render(request, template, context)

@login_required
def add_comment(request, app_label, model_name, object_id):
    """Add a new comment"""
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            except ContentType.DoesNotExist:
                messages.error(request, 'Invalid content type.')
                return redirect('/')
            
            comment = form.save(commit=False)
            comment.author = request.user
            comment.content_type = content_type
            comment.object_id = object_id
            comment.user_ip = get_client_ip(request)
            comment.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            comment.save()
            
            # Auto-approve for trusted users
            if request.user.is_superuser or request.user.has_perm('comments.auto_approve_comments'):
                comment.approve()
            
            messages.success(request, 'Your comment has been posted!')
            
            # Get the original object URL
            obj = content_type.get_object_for_this_type(id=object_id)
            if hasattr(obj, 'get_absolute_url'):
                return redirect(obj.get_absolute_url())
    
    return redirect('/')

@login_required
def edit_comment(request, comment_id):
    """Edit an existing comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check permission
    if comment.author != request.user and not is_moderator(request.user):
        messages.error(request, 'You do not have permission to edit this comment.')
        return redirect('/')
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your comment has been updated!')
            
            # Get the original object URL
            obj = comment.content_object
            if hasattr(obj, 'get_absolute_url'):
                return redirect(obj.get_absolute_url())
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'comments/comment_edit.html', {
        'form': form,
        'comment': comment
    })

@login_required
def delete_comment(request, comment_id):
    """Delete a comment (soft delete)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check permission
    if comment.author != request.user and not is_moderator(request.user):
        messages.error(request, 'You do not have permission to delete this comment.')
        return redirect('/')
    
    if request.method == 'POST':
        if is_moderator(request.user):
            comment.delete_comment(request.user)
            messages.success(request, 'Comment has been deleted by moderator.')
        else:
            comment.status = 'deleted'
            comment.content = '[This comment has been deleted by the author]'
            comment.save()
            messages.success(request, 'Your comment has been deleted.')
        
        # Get the original object URL
        obj = comment.content_object
        if hasattr(obj, 'get_absolute_url'):
            return redirect(obj.get_absolute_url())
    
    return render(request, 'comments/comment_confirm_delete.html', {'comment': comment})

@login_required
def add_reply(request, comment_id):
    """Add a reply to a comment"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.author = request.user
            reply.parent = parent_comment
            reply.content_type = parent_comment.content_type
            reply.object_id = parent_comment.object_id
            reply.user_ip = get_client_ip(request)
            reply.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            reply.save()
            
            # Auto-approve for trusted users
            if request.user.is_superuser or request.user.has_perm('comments.auto_approve_comments'):
                reply.approve()
            
            messages.success(request, 'Your reply has been posted!')
            
            # Get the original object URL
            obj = reply.content_object
            if hasattr(obj, 'get_absolute_url'):
                return redirect(obj.get_absolute_url())
    
    return redirect('/')

@login_required
def like_comment(request, comment_id):
    """Like/unlike a comment (AJAX)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    like, created = CommentLike.objects.get_or_create(
        comment=comment,
        user=request.user
    )
    
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    
    # Update comment like count
    comment.likes = comment.likes_info.count()
    comment.save()
    
    return JsonResponse({
        'liked': liked,
        'likes_count': comment.likes
    })

@login_required
def report_comment(request, comment_id):
    """Report an inappropriate comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Can't report own comment
    if comment.author == request.user:
        messages.error(request, 'You cannot report your own comment.')
        return redirect('/')
    
    # Check if already reported
    if CommentReport.objects.filter(comment=comment, reporter=request.user).exists():
        messages.error(request, 'You have already reported this comment.')
        return redirect('/')
    
    if request.method == 'POST':
        form = CommentReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.comment = comment
            report.reporter = request.user
            report.save()
            
            # Increment report count
            comment.reports += 1
            comment.save()
            
            messages.success(request, 'Thank you for reporting. A moderator will review this comment.')
            
            # Get the original object URL
            obj = comment.content_object
            if hasattr(obj, 'get_absolute_url'):
                return redirect(obj.get_absolute_url())
    else:
        form = CommentReportForm()
    
    return render(request, 'comments/comment_report.html', {
        'form': form,
        'comment': comment
    })

@login_required
def subscribe_to_thread(request, content_type, object_id):
    """Subscribe to comment thread notifications"""
    content_type_obj = ContentType.objects.get(app_label=content_type, model=content_type)
    
    subscription, created = CommentSubscription.objects.get_or_create(
        user=request.user,
        content_type=content_type_obj,
        object_id=object_id
    )
    
    if created:
        messages.success(request, 'You have subscribed to this discussion.')
    else:
        subscription.delete()
        messages.success(request, 'You have unsubscribed from this discussion.')
    
    # Get the original object URL
    obj = content_type_obj.get_object_for_this_type(id=object_id)
    if hasattr(obj, 'get_absolute_url'):
        return redirect(obj.get_absolute_url())
    
    return redirect('/')

@user_passes_test(is_moderator)
@user_passes_test(is_moderator)
def moderation_dashboard(request):
    """Moderation dashboard for managing comments"""
    # Get all pending comments
    pending_comments = Comment.objects.filter(status='pending').select_related('author', 'content_type')
    
    # Get reported comments
    reported_comments = Comment.objects.filter(
        reports__gt=0,
        status__in=['approved', 'pending']
    ).distinct().select_related('author', 'content_type')
    
    # Search and filter
    form = CommentSearchForm(request.GET)
    if form.is_valid():
        q = form.cleaned_data.get('q')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if q:
            pending_comments = pending_comments.filter(content__icontains=q)
            reported_comments = reported_comments.filter(content__icontains=q)
        if status:
            pending_comments = pending_comments.filter(status=status)
        if date_from:
            pending_comments = pending_comments.filter(created_at__date__gte=date_from)
            reported_comments = reported_comments.filter(created_at__date__gte=date_from)
        if date_to:
            pending_comments = pending_comments.filter(created_at__date__lte=date_to)
            reported_comments = reported_comments.filter(created_at__date__lte=date_to)
    
    # Pagination
    pending_paginator = Paginator(pending_comments, 10)
    pending_page = request.GET.get('pending_page', 1)
    pending_comments_page = pending_paginator.get_page(pending_page)
    
    reported_paginator = Paginator(reported_comments, 10)
    reported_page = request.GET.get('reported_page', 1)
    reported_comments_page = reported_paginator.get_page(reported_page)
    
    context = {
        'pending_comments': pending_comments_page,
        'reported_comments': reported_comments_page,
        'form': form,
    }
    return render(request, 'comments/moderation.html', context)

@user_passes_test(is_moderator)
def moderate_comment(request, comment_id, action):
    """Approve, mark as spam, or delete a comment"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if action == 'approve':
        comment.approve(request.user)
        messages.success(request, f'Comment by {comment.author.username} has been approved.')
    elif action == 'spam':
        comment.mark_as_spam(request.user)
        messages.success(request, f'Comment by {comment.author.username} has been marked as spam.')
    elif action == 'delete':
        comment.delete_comment(request.user)
        messages.success(request, f'Comment by {comment.author.username} has been deleted.')
    
    return redirect('comments:moderation_dashboard')

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def comment_detail(request, comment_id):
    """View single comment details"""
    comment = get_object_or_404(Comment, id=comment_id)
    return render(request, 'comments/comment_detail.html', {'comment': comment})



def get_comment_reports_api(request, comment_id):
    """API endpoint to get reports for a comment (AJAX)"""
    comment = get_object_or_404(Comment, id=comment_id)
    reports = CommentReport.objects.filter(comment=comment).values(
        'reporter__username', 'reason', 'details', 'created_at'
    )
    
    data = []
    for report in reports:
        data.append({
            'reporter': report['reporter__username'],
            'reason': report['reason'],
            'details': report['details'],
            'created_at': report['created_at'].isoformat()
        })
    
    return JsonResponse(data, safe=False)