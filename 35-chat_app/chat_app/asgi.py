import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

# Import consumers after Django setup
from chat import consumers

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/chat/<str:room_slug>/', consumers.ChatConsumer.as_asgi()),
        ])
    ),
})