from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # ইউজার অথেনটিকেট চেক
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        try:
            profile = await self.get_profile(user)
        except Exception:
            await self.close()
            return

        # মেসেজ সেভ করুন
        await self.save_message(profile, self.room_id, message)

        # গ্রুপে মেসেজ পাঠান
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': profile.user.username,  # username পাঠাচ্ছি
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
        }))

    @database_sync_to_async
    def get_profile(self, user):
        # ইউজারের প্রোফাইল রিটার্ন করবে
        return user.profile

    @database_sync_to_async
    def save_message(self, profile, room_id, message):
        try:
            room = ChatRoom.objects.get(id=room_id)
        except ChatRoom.DoesNotExist:
            return

        Message.objects.create(
            chat_room=room,
            user=profile,
            content=message
        )
