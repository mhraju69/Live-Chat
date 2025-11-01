from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.db import database_sync_to_async, sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message 
from django.contrib.auth.models import AnonymousUser
from User.models import *
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # User authentication check
        user = self.scope["user"]
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        user = self.scope["user"]
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return

        try:
            profile = await self.get_profile(user)
            room = await self.get_room(self.room_id)
        except Exception as e:
            print(f"Error: {e}")
            await self.close()
            return

        # Save message
        await self.save_message(profile, room, message)

        # Get all participants in the room except sender
        participants = await self.get_room_participants(room, user)

        # Send chat message to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': profile.user.username,
                'sender_id': user.id
            }
        )

        # Send notifications to all participants except sender
        for participant in participants:
            await self.channel_layer.group_send(
                f'notifications_{participant.id}',
                {
                    'type': 'send_notification',
                    'message': message,
                    'sender': profile.user.username,
                    'room_id': self.room_id,
                    'sound': True
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'sender_id': event['sender_id']
        }))

    @database_sync_to_async
    def get_profile(self, user):
        return user.profile

    @database_sync_to_async
    def get_room(self, room_id):
        return ChatRoom.objects.get(id=room_id)

    @database_sync_to_async
    def save_message(self, profile, room, message):
        Message.objects.create(
            chat_room=room,
            user=profile,
            content=message
        )

    @database_sync_to_async
    def get_room_participants(self, room, exclude_user):
        # This assumes you have a way to get participants in a room
        # Adjust according to your model structure
        participants = room.members.exclude(id=exclude_user.id)
        return list(participants)

class SimpleRTCConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # URL থেকে room_name
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"room_{self.room_name}"

        # গ্রুপে যোগ
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # অন্যদের জানানো যে নতুন peer যোগ হয়েছে
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "peer_join",
                "sender": self.channel_name
            }
        )

    async def disconnect(self, close_code):
        # গ্রুপ থেকে বের হওয়া
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "peer_leave",
                "sender": self.channel_name
            }
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        payload = data.get("payload")

        # দুইজনের মধ্যে signaling message পাঠানো
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "signaling_message",
                "action": action,
                "payload": payload,
                "sender": self.channel_name
            }
        )

    # ---------------- Handlers ----------------
    async def signaling_message(self, event):
        # নিজেকে message পাঠাবো না
        if event['sender'] == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            "action": event['action'],
            "payload": event['payload'],
            "from": event['sender']
        }))

    async def peer_join(self, event):
        if event['sender'] == self.channel_name:
            return
        await self.send(text_data=json.dumps({
            "action": "peer-joined",
            "payload": {"channel": event['sender']}
        }))

    async def peer_leave(self, event):
        await self.send(text_data=json.dumps({
            "action": "peer-left",
            "payload": {"channel": event['sender']}
        }))
