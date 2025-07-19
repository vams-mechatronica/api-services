from .clients.infobip_client import InfobipWhatsAppClient

class WhatsAppGateway:
    """
    Manages WhatsApp template-based messaging via Infobip:
    - OTP delivery
    - Marketing notifications
    - Order updates
    """

    def __init__(self, client=None):
        """
        :param client: Inject Infobip client.
        """
        self.client = InfobipWhatsAppClient if not client else client

    def send_otp(self, phone_number, otp_code):
        template_id = 'otp_template_id'
        parameters = [otp_code, "5 minutes"]  # Example: [OTP, Expiry Time]
        return self._send_template(phone_number, template_id, parameters)

    def send_marketing_message(self, phone_number, template_id, parameters):
        return self._send_template(phone_number, template_id, parameters)

    def send_order_update(self, phone_number, template_id, parameters):
        return self._send_template(phone_number, template_id, parameters)

    def _send_template(self, phone_number, template_id, parameters):
        """
        Internal method to send WhatsApp template message.
        """
        return self.client().send_template_message(
            to=phone_number,
            template_id=template_id,
            parameters=parameters
        )
