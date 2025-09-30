from .base import BaseNotifier
from utils.whatsapp.whatsapp_gateway import WhatsAppGateway

class WhatsAppNotifier(BaseNotifier):
    def send(self, user, message):
        WhatsAppGateway().send(user.phone, message)
    
    def send_marketing_message(self, user, message_id):
        WhatsAppGateway.send_marketing_message(user.phone, message_id, parameters=None)
