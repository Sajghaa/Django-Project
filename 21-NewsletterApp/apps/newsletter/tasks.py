from celery import shared_task
from django.utils import timezone
from .models import Newsletter
from .utils import send_newsletter_to_subscribers

@shared_task
def send_scheduled_newsletters():
    """Send scheduled newsletters"""
    newsletters = Newsletter.objects.filter(
        status='scheduled',
        scheduled_for__lte=timezone.now()
    )
    
    for newsletter in newsletters:
        send_newsletter_to_subscribers(newsletter)

@shared_task
def send_confirmation_email(subscriber_id):
    """Send confirmation email asynchronously"""
    from .models import Subscriber
    try:
        subscriber = Subscriber.objects.get(id=subscriber_id)
        subscriber.send_confirmation_email()
    except Subscriber.DoesNotExist:
        pass