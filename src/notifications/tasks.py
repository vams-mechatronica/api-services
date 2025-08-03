# notifications/tasks.py
from celery import shared_task
from django.contrib.auth import get_user_model
from notifications.manager import NotifierManager

User = get_user_model()

@shared_task
def async_notify(user_id, message):
    user = User.objects.get(id=user_id)
    NotifierManager().notify(user, message)
