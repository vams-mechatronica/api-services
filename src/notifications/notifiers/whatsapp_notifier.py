from .base import BaseNotifier
from utils.whatsapp.whatsapp_gateway import WhatsAppGateway

class WhatsAppNotifier(BaseNotifier):
    def send(self, user, message):
        WhatsAppGateway().send(user.phone, message)
