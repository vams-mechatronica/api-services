from .base import MessageService

class OTPService:
    """Handles OTP generation & delivery (delegates sending)."""

    def __init__(self, message_service: MessageService):
        self._message_service = message_service

    def send_otp(self, to: str, otp: str) -> str:
        """Send OTP message using injected service."""
        body = f"Your verification code is {otp}. It will expire in 5 minutes."
        return self._message_service.send_message(to, body)