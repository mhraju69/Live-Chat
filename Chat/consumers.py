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

    # Notification handler (for cases where the user is also connected to notifications)
    async def send_notification(self, event):
        # Only send if the user is not the sender
        if self.scope["user"].id != event.get('sender_id', None):
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'message': event['message'],
                'sender': event['sender'],
                'room_id': event['room_id'],
                'sound': event['sound']
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

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f"call_{self.room_id}"

        # গ্রুপে নিজেকে যোগ দাও
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # গ্রুপ থেকে নিজেকে রিমুভ করো
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        # মেসেজ টাইপ, কন্ডিডেট বা এসডিপি ইত্যাদি থাকবে এখানে
        # গ্রুপের সবাইকে মেসেজ পাঠাও
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "signaling.message",
                "message": data,
            }
        )

    async def signaling_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps(message))

class NotificationConsumer(AsyncWebsocketConsumer):

    def otherUser(request,self):
        room_id = self.scope['url_route']['kwargs']['room_id']
        room = ChatRoom.objects.get(id=room_id)
        profile = request.user.profile
        other = room.members.exclude(id=profile.id).first()
        other_profile = other if other else profile
        return other_profile

    async def connect(self):
        user = self.scope["user"]
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return
       
        self.user_id = user.id
        self.notification_group_name = f'notifications_{self.user_id}'

        # Get user profile if exists
        try:
            

            self.profile = await sync_to_async(getattr)(user, 'profile', None)
        except Exception:
            self.profile = None
        
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.notification_group_name,
            self.channel_name
        )
    
    async def send_notification(self, event):
        sender_name = event.get('sender_profile_name') or event.get('sender') or "Unknown"

        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'sender': sender_name,              # the human-readable name you want
            'sender_username': event.get('sender'),
            'room_id': event.get('room_id'),
            'sound': event.get('sound', True),
            'avatar': event.get('avatar', '/static/images/message.png')
        }))


from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_room_users(room, sender, message):
    channel_layer = get_channel_layer()

    # Get sender profile name
    try:
        sender_profile_name = sender.profile.name
    except Exception:
        sender_profile_name = sender.username  # fallback

    # For all users in the room except sender:
    participants = room.users.exclude(id=sender.id)  # adjust depending on your model

    for user in participants:
        group_name = f'notifications_{user.id}'

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': message,
                'sender': sender.username,
                'sender_profile_name': sender_profile_name,
                'room_id': room.id,
                'sound': True,
                'avatar': sender.profile.avatar.url if hasattr(sender.profile, 'avatar') else '/static/images/message.png'
            }
        )
