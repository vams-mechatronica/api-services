from .models import *
from django.utils import timezone
from datetime import timedelta
from random import randint
from utils.whatsapp.whatsapp_gateway import WhatsAppGateway

class OTPService:

    @staticmethod
    def generate_random_otp():
        return str(randint(100000,999999))
    
    @staticmethod
    def generate_otp(phone_number):
        otp_code = OTPService.generate_random_otp()
        expires_at = timezone.now() + timedelta(minutes=5)
        OTPRecord.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at
        )
        WhatsAppGateway().send_otp(phone_number, otp_code)
        return otp_code

    @staticmethod
    def verify_otp(phone_number, otp_code):
        record = OTPRecord.objects.filter(phone_number=phone_number, otp_code=otp_code).last()
        if record and not record.is_expired():
            record.is_verified = True
            record.save()
            return True
        return False
