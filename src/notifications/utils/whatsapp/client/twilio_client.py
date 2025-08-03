# whatsapp/client/twilio_client.py
import requests
from ..base.base_client import WhatsAppBaseClient
from django.conf import settings
from requests.auth import HTTPBasicAuth

class TwilioWhatsAppClient(WhatsAppBaseClient):
    def __init__(self):
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.sender_number = settings.TWILIO_WHATSAPP_NUMBER

    def send_template_message(self, to, template_id_or_text, parameters=None):
        to_number = f"whatsapp:{to}"
        from_number = f"whatsapp:{self.sender_number}"

        message_body = template_id_or_text.format(*parameters) if parameters else template_id_or_text

        payload = {
            "To": to_number,
            "From": from_number,
            "Body": message_body,
        }

        response = requests.post(
            self.base_url,
            data=payload,
            auth=HTTPBasicAuth(self.account_sid, self.auth_token),
        )

        if response.status_code in [200, 201]:
            return response.json()
        raise Exception(f"Twilio Error {response.status_code}: {response.text}")
