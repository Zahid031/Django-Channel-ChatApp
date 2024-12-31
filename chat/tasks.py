from celery import shared_task
from django.utils import timezone
from .models import Message
import os

@shared_task
def delete_expired_files():
    expired_messages = Message.objects.filter(
        file__isnull=False,
        file_expiry__lte=timezone.now()
    )
    
    for message in expired_messages:
        if message.file and os.path.isfile(message.file.path):
            try:
                os.remove(message.file.path)
            except OSError:
                pass
        message.file = None
        message.file_expiry = None
        message.save()