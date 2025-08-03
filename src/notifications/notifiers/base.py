# notifications/notifiers/base.py
from notifications.interfaces import BaseNotifier

class DummyNotifier(BaseNotifier):
    def send(self, user, message):
        print(f"Notify {user.email}: {message}")
