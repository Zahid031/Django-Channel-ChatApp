from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message, Group, Conversation

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ('id', 'name', 'members', 'created_at')

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = ('id', 'sender', 'message', 'file', 'file_url', 'timestamp', 'file_expiry')
        read_only_fields = ('file_expiry',)
    
    def get_file_url(self, obj):
        if obj.file:
            return self.context['request'].build_absolute_uri(obj.file.url)
        return None

class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    group = GroupSerializer(read_only=True)
    last_message = MessageSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'group', 'last_message', 'updated_at')