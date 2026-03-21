from django.apps import AppConfig

class NewsletterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.newsletter'
    label = 'newsletter'
    
    def ready(self):
        # Import signals if you have any
        pass