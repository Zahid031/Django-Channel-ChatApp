import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message, Group
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        file_url = data.get('file', '')

        # Save message to database
        await self.save_message(message, file_url)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'file': file_url,
                'sender': self.user.username
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'file': event['file'],
            'sender': event['sender']
        }))

    @database_sync_to_async
    def save_message(self, message_text, file_url):
        is_group = hasattr(self, 'room_group_name') and 'group' in self.room_group_name
        
        if is_group:
            group = Group.objects.get(id=self.room_id)
            Message.objects.create(
                sender=self.user,
                receiver_group=group,
                message=message_text,
                file=file_url if file_url else None
            )
        else:
            receiver = User.objects.get(id=self.room_id)
            Message.objects.create(
                sender=self.user,
                receiver_user=receiver,
                message=message_text,
                file=file_url if file_url else None
            )