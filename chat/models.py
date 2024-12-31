from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

def get_file_path(instance, filename):
    return f'chat_files/{instance.sender.username}/{filename}'

class Group(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name='chat_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    receiver_group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='group_messages', null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to=get_file_path, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    file_expiry = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.file and not self.file_expiry:
            self.file_expiry = timezone.now() + timezone.timedelta(days=10)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-timestamp']

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    last_message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, related_name='+')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']