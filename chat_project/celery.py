import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

app = Celery('chat_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'delete-expired-files': {
        'task': 'chat.tasks.delete_expired_files',
        'schedule': 3600.0,  # Run every hour
    },
}