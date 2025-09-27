# notifications/services.py
from django.conf import settings
from notifications.backends.db_backend import DatabaseMessageQueueBackend
# or CeleryMessageQueueBackend later

backend = DatabaseMessageQueueBackend()  # inject based on settings

def enqueue_message(recipient, subject, body, channel='email'):
    backend.enqueue(recipient, subject, body, channel)

def process_pending_messages():
    backend.process_pending()
