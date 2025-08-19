from abc import ABC, abstractmethod

# -----------------------------
# Interface (Dependency Inversion)
# -----------------------------
class MessageService(ABC):
    """Abstract interface for sending messages."""

    @abstractmethod
    def send_message(self, to: str, body: str) -> str:
        """Send a message and return message SID or ID."""
        pass
