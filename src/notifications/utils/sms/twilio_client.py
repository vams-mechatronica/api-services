from .base import MessageService
from twilio.rest import Client

class TwilioSMSService(MessageService):
    """Concrete implementation for sending SMS via Twilio."""

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self._client = Client(account_sid, auth_token)
        self._from_number = from_number

    def send_message(self, to: str, body: str) -> str:
        """Send SMS using Twilio API."""
        message = self._client.messages.create(
            body=body,
            from_=self._from_number,
            to=to
        )
        return message.sid