import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        
        print(f"=== WebSocket Connecting to room: {self.room_slug} ===")
        print(f"User: {self.scope['user']}")
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        print("=== WebSocket Connected! ===")
        
        # Send a welcome message
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': f'Welcome to the room!',
            'username': 'System',
            'user_id': 0,
            'timestamp': 'Just now',
            'time_ago': 'Just now'
        }))
    
    async def disconnect(self, close_code):
        print(f"=== WebSocket Disconnected: {close_code} ===")
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        print(f"=== Received message: {text_data} ===")
        
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username if user.is_authenticated else 'Anonymous',
                'user_id': user.id if user.is_authenticated else 0,
                'timestamp': 'Just now',
                'time_ago': 'Just now'
            }
        )
    
    async def chat_message(self, event):
        print(f"=== Broadcasting: {event} ===")
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'time_ago': event['time_ago']
        }))