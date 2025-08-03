# notifications/interfaces.py
from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    @abstractmethod
    def send(self, user, message): pass
