from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from User.models import *

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    members = models.ManyToManyField(Profile, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name or ""
    
    def get_display_name(self, current_user_profile):

        other_members = self.members.exclude(id=current_user_profile.id)

        if other_members.exists():
            return other_members.first().user.get_full_name() or other_members.first().user.username
        else:
            return current_user_profile.user.get_full_name() or current_user_profile.user.username        


class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name}: {self.content[:20]}"

    class Meta:
        ordering = ['timestamp']

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(Profile, related_name='chat_group')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name