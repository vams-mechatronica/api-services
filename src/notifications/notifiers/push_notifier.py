from .base import BaseNotifier
from utils.push_client import PushClient

class PushNotifier(BaseNotifier):
    def send(self, user, message):
        if hasattr(user, 'fcm_token') and user.fcm_token:
            push = PushClient(
                title="Notification",
                body=message,
                token_list=user.fcm_token  # should be a string or list
            )
            push.send()
