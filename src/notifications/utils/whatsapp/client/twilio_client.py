# whatsapp/client/twilio_client.py
import requests
from ..base.base_client import WhatsAppBaseClient
from django.conf import settings
from requests.auth import HTTPBasicAuth
from twilio.rest import Client
import json

class TwilioWhatsAppClient(WhatsAppBaseClient):
    def __init__(self):
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.sender_number = settings.TWILIO_WHATSAPP_NUMBER

    def send_template_message(self, to, template_id_or_text, parameters=None):
        to_number = f"whatsapp:{to}"
        from_number = f"whatsapp:{self.sender_number}"
        client = Client(self.account_sid, self.auth_token)
        if not parameters:
            message = client.messages.create(
            from_=from_number,
            to=to_number,
            content_sid=template_id_or_text
            )
        else:
            message = client.messages.create(
                from_=from_number,
                to=to_number,
                content_sid=template_id_or_text,
                content_variables=json.dumps({'1':parameters[0]}) if isinstance(parameters, list) else ''
            )
        return message.body
