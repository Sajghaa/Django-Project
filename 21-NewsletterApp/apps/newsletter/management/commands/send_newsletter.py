from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.newsletter.models import Newsletter
from apps.newsletter.utils import send_newsletter_to_subscribers

class Command(BaseCommand):
    help = 'Send scheduled newsletters'
    
    def handle(self, *args, **options):
        newsletters = Newsletter.objects.filter(
            status='scheduled',
            scheduled_for__lte=timezone.now()
        )
        
        for newsletter in newsletters:
            self.stdout.write(f'Sending newsletter: {newsletter.subject}')
            send_newsletter_to_subscribers(newsletter)
            self.stdout.write(self.style.SUCCESS(f'Successfully sent: {newsletter.subject}'))