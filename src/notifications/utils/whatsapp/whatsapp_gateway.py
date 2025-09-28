from .client.infobip_client import InfobipWhatsAppClient
from .client.twilio_client import TwilioWhatsAppClient
import logging

logger = logging.getLogger(__name__)
class WhatsAppGateway:
    """
    Manages WhatsApp template-based messaging via Infobip:
    - OTP delivery
    - Marketing notifications
    - Order updates
    """
    def __init__(self, clients=None):
        self.clients = TwilioWhatsAppClient()

    def send_otp(self, phone_number, otp_code):
        template_id = 'HX9e95162bc897e570e1f0f772e7a9dc33'
        parameters = [otp_code, "5 minutes"]
        return self.clients.send_template_message(phone_number, template_id, parameters)

    def send_marketing_message(self, phone_number, template_id_or_text, parameters):
        return self._send_with_failover(phone_number, template_id_or_text, parameters)

    def send_order_update(self, phone_number, template_id_or_text, parameters):
        return self._send_with_failover(phone_number, template_id_or_text, parameters)
    
    def send(self, phone_number, template_id_or_text, parameters=None):
        return self._send_with_failover(phone_number, template_id_or_text, parameters)

    def _send_with_failover(self, phone_number, template_id_or_text, parameters):
        for client in self.clients:
            try:
                return client.send_template_message(phone_number, template_id_or_text, parameters)
            except Exception as e:
                logger.exception(f"Failed with {client.__class__.__name__}: {e}")
        raise Exception("All WhatsApp clients failed to send the message.")
