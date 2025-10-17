from abc import ABC, abstractmethod
from typing import List, Dict

class EmailBaseClient(ABC):
    @abstractmethod
    def send_template_message(self, to_email: str, subject: str, template: str, context: Dict):
        """Send a single template email."""
        pass

    @abstractmethod
    def send_template_message_bulk(self, recipients: List[Dict]):
        """Send bulk template emails to multiple recipients."""
        pass