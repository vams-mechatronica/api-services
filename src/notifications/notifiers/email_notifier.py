# notifications/notifiers/email_notifier.py
from .base import BaseNotifier
from utils.email_client import EmailClient

class EmailNotifier(BaseNotifier):
    def send(self, user, message):
        if user.email:
            email = EmailClient(
                subject="Subscription Created",
                to_emails=user.email,
                body=message
            )
            email.send()
