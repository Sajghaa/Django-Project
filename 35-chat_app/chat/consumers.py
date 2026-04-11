import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import ChatRoom, Message, UserStatus
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for chat functionality"""
    
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        
        print(f"WebSocket connecting to room: {self.room_slug}")
        print(f"User: {self.scope['user']}")
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        print(f"WebSocket connected to room: {self.room_slug}")
        
        # Update user status
        await self.update_user_status(True, self.room_slug)
        
        # Send online users list
        await self.send_online_users()
    
    async def disconnect(self, close_code):
        print(f"WebSocket disconnected from room: {self.room_slug}")
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Update user status
        await self.update_user_status(False, None)
        
        # Send online users list
        await self.send_online_users()
    
    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'message')
        
        if message_type == 'message':
            message = text_data_json['message']
            user = self.scope['user']
            
            print(f"User {user.username} sent message: {message}")
            
            # Save message to database
            saved_message = await self.save_message(user, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': user.username,
                    'user_id': user.id,
                    'timestamp': saved_message['timestamp'],
                    'time_ago': saved_message['time_ago']
                }
            )
        
        elif message_type == 'typing':
            user = self.scope['user']
            is_typing = text_data_json.get('is_typing', False)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'username': user.username,
                    'is_typing': is_typing
                }
            )
    
    async def chat_message(self, event):
        print(f"Broadcasting message: {event}")
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'username': event['username'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'time_ago': event['time_ago']
        }))
    
    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'username': event['username'],
            'is_typing': event['is_typing']
        }))
    
    async def online_users(self, event):
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'users': event['users']
        }))
    
    @database_sync_to_async
    def save_message(self, user, message):
        """Save message to database"""
        try:
            room = ChatRoom.objects.get(slug=self.room_slug)
            msg = Message.objects.create(
                room=room,
                user=user,
                content=message
            )
            print(f"Message saved to database: {msg.id}")
            return {
                'timestamp': msg.created_at.strftime('%I:%M %p'),
                'time_ago': msg.time_ago
            }
        except Exception as e:
            print(f"Error saving message: {e}")
            return {'timestamp': 'Just now', 'time_ago': 'Just now'}
    
    @database_sync_to_async
    def update_user_status(self, is_online, current_room):
        """Update user online status"""
        user = self.scope['user']
        if user and user.is_authenticated:
            status, created = UserStatus.objects.get_or_create(user=user)
            status.is_online = is_online
            status.current_room = current_room
            status.last_activity = datetime.now()
            status.save()
            print(f"User {user.username} status updated: {'Online' if is_online else 'Offline'}")
    
    @database_sync_to_async
    def get_online_users(self):
        """Get list of online users in the room"""
        try:
            online_statuses = UserStatus.objects.filter(
                is_online=True,
                current_room=self.room_slug
            ).select_related('user')
            
            users = []
            for status in online_statuses:
                users.append({
                    'id': status.user.id,
                    'username': status.user.username,
                    'avatar': None
                })
            return users
        except Exception as e:
            print(f"Error getting online users: {e}")
            return []
    
    async def send_online_users(self):
        """Send online users list to all clients in room"""
        users = await self.get_online_users()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'online_users',
                'users': users
            }
        )