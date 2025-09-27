# notifications/interfaces.py
from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @abstractmethod
    def send(self, user, message): pass

class MessageQueueBackend(ABC):
    @abstractmethod
    def enqueue(self, recipient: str, subject: str, body: str, channel: str = 'email'):
        """Add a message to the queue."""

    @abstractmethod
    def process_pending(self):
        """Process pending messages."""
