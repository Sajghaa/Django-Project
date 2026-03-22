from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import uuid

def generate_tracking_pixel(newsletter_id, subscriber_id):
    """Generate tracking pixel URL"""
    return f"{settings.SITE_URL}/newsletter/track/open/{newsletter_id}/{subscriber_id}/pixel.png"

def generate_tracking_link(newsletter_id, subscriber_id, url):
    """Generate tracking link URL"""
    return f"{settings.SITE_URL}/newsletter/track/click/{newsletter_id}/{subscriber_id}/?url={url}"

def send_newsletter_to_subscribers(newsletter):
    """Send newsletter to all active subscribers"""
    from .models import Subscriber
    
    subscribers = Subscriber.objects.filter(status='active')
    
    sent_count = 0
    for subscriber in subscribers:
        try:
            # Prepare context
            context = {
                'newsletter': newsletter,
                'subscriber': subscriber,
                'tracking_pixel': generate_tracking_pixel(newsletter.id, subscriber.id) if newsletter.track_opens else None,
            }
            
            # Generate HTML with tracking links
            html_content = newsletter.html_content or newsletter.content
            if newsletter.track_clicks:
                # Replace links with tracking links
                import re
                url_pattern = re.compile(r'href=["\'](https?://[^"\']+)["\']')
                
                def replace_url(match):
                    original_url = match.group(1)
                    tracking_url = generate_tracking_link(newsletter.id, subscriber.id, original_url)
                    return f'href="{tracking_url}"'
                
                html_content = url_pattern.sub(replace_url, html_content)
            
            context['content'] = html_content
            
            html_message = render_to_string('newsletter/emails/newsletter.html', context)
            plain_message = strip_tags(newsletter.content)
            
            send_mail(
                newsletter.subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [subscriber.email],
                html_message=html_message,
                fail_silently=False,
            )
            sent_count += 1
            
        except Exception as e:
            print(f"Failed to send to {subscriber.email}: {e}")
    
    # Update newsletter stats
    newsletter.sent_to_count = sent_count
    newsletter.sent_at = timezone.now()
    newsletter.status = 'sent'
    newsletter.save()