# notifications/manager.py
import threading
from notifications.notifiers.email_notifier import EmailNotifier
from notifications.notifiers.whatsapp_notifier import WhatsAppNotifier
from notifications.notifiers.push_notifier import PushNotifier

class NotifierManager:
    def __init__(self):
        self.notifiers = [
            EmailNotifier(),
            WhatsAppNotifier(),
            PushNotifier()
        ]

    def notify(self, user, message):
        for notifier in self.notifiers:
            threading.Thread(target=notifier.send, args=(user, message)).start()
