from django.utils import timezone
from datetime import timedelta
from .models import Task, Reminder
from django.core.mail import send_mail
from django.conf import settings

def check_upcoming_tasks():
    """Check for upcoming tasks and send reminders"""
    now = timezone.now()
    upcoming_threshold = now + timedelta(hours=24)
    
    # Get tasks due in next 24 hours
    upcoming_tasks = Task.objects.filter(
        due_date__gte=now,
        due_date__lte=upcoming_threshold,
        status__in=['pending', 'in_progress'],
        reminder_sent=False
    )
    
    for task in upcoming_tasks:
        # Create reminder record
        reminder = Reminder.objects.create(
            task=task,
            reminder_time=task.due_date - timedelta(hours=1),
            reminder_type='email'
        )
        
        # Send email reminder
        send_mail(
            subject=f'Task Reminder: {task.title}',
            message=f'Your task "{task.title}" is due on {task.due_date.strftime("%Y-%m-%d %H:%M")}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[task.user.email],
            fail_silently=True,
        )
        
        task.reminder_sent = True
        task.save()

def get_task_stats(user):
    """Get task statistics for dashboard"""
    tasks = Task.objects.filter(user=user)
    
    stats = {
        'total': tasks.count(),
        'completed': tasks.filter(status='completed').count(),
        'pending': tasks.filter(status='pending').count(),
        'in_progress': tasks.filter(status='in_progress').count(),
        'overdue': tasks.filter(due_date__lt=timezone.now()).exclude(status='completed').count(),
        'high_priority': tasks.filter(priority__in=['high', 'urgent']).count(),
    }
    
    # Calculate completion rate
    if stats['total'] > 0:
        stats['completion_rate'] = int((stats['completed'] / stats['total']) * 100)
    else:
        stats['completion_rate'] = 0
    
    return stats

def get_upcoming_tasks(user, days=7):
    """Get tasks due in next N days"""
    now = timezone.now()
    future = now + timedelta(days=days)
    
    return Task.objects.filter(
        user=user,
        due_date__gte=now,
        due_date__lte=future,
        status__in=['pending', 'in_progress']
    ).order_by('due_date')

def get_overdue_tasks(user):
    """Get overdue tasks"""
    return Task.objects.filter(
        user=user,
        due_date__lt=timezone.now(),
        status__in=['pending', 'in_progress']
    ).order_by('due_date')