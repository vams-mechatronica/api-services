import requests
from .base_client import WhatsAppBaseClient
from django.conf import settings
from utils.g_uuid import GenerateUUID
from requests.auth import HTTPBasicAuth

class InfobipWhatsAppClient(WhatsAppBaseClient):
    def __init__(self):
        self.base_url = settings.INFOBIP_BASE_URL
        self.api_key = settings.INFOBIP_API_KEY
        self.sender_number = settings.INFOBIP_SENDER_NUMBER

    def send_template_message(self, to, template_id, parameters):
        url = f"{self.base_url}/whatsapp/1/message/template"

        payload = {
            "messages": [
                {
                "from": self.sender_number,
                "to": to,
                "messageId": GenerateUUID.generate_whatsapp_otp_message_id(),
                "content": {
                    "templateName": "otp_auth_wa",
                    "templateData": {
                    "body": {
                        "placeholders": [
                        str(parameters[0])
                        ]
                    },
                    "buttons": [
                        {
                        "type": "URL",
                        "parameter": str(parameters[0])
                        }
                    ]
                    },
                    "language": "en_GB"
                },
                "callbackData": "Callback data",
                "notifyUrl": "https://www.vamsconnect.com/api/v1/whatsapp/delivery-status/add"
                }
            ]
        }

        headers = {
            "Authorization": f"App {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Infobip Error {response.status_code}: {response.text}")
        # return response.text()


class TwilioWhatsAppClient(WhatsAppBaseClient):
    def __init__(self):
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.sender_number = settings.TWILIO_WHATSAPP_NUMBER

    def send_template_message(self, to, template_text, parameters=None):
        """
        Note: Twilio doesn't support dynamic WhatsApp template rendering like Infobip.
        You must use pre-approved templates, so you'll need to replace placeholders yourself.
        """
        to_number = f"whatsapp:{to}"
        from_number = f"whatsapp:{self.sender_number}"

        if parameters:
            message_body = template_text.format(*parameters)
        else:
            message_body = template_text

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
        else:
            raise Exception(f"Twilio Error {response.status_code}: {response.text}")
