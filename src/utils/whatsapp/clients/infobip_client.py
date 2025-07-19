import requests
from .base_client import WhatsAppBaseClient
from django.conf import settings
from utils.g_uuid import GenerateUUID

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
