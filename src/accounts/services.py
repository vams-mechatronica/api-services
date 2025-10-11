from .models import *
from django.utils import timezone
from datetime import timedelta
from random import randint
from notifications.utils.whatsapp.whatsapp_gateway import WhatsAppGateway
from notifications.utils.sms.twilio_client import TwilioSMSService
from notifications.utils.sms.services import OTPService as Twilio_OTPService
from django.conf import settings

class OTPService:

    @staticmethod
    def generate_random_otp():
        return str(randint(1000,9999))
    
    @staticmethod
    def generate_otp(phone_number, send_as_sms=None):
        now = timezone.now()
        last_otp = (
            OTPRecord.objects
            .filter(phone_number=phone_number)
            .order_by('-created_at')
            .first()
        )

        if last_otp and (now - last_otp.created_at) < timedelta(seconds=60):
            return last_otp.otp_code

        otp_code = OTPService.generate_random_otp()
        expires_at = now + timedelta(minutes=5)
        OTPRecord.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            expires_at=expires_at
        )
        if not send_as_sms:
            WhatsAppGateway().send_otp(phone_number, otp_code)
        else:
            sms_service = TwilioSMSService(settings.TWILIO_ACCOUNT_SID,\
                                            settings.TWILIO_AUTH_TOKEN,\
                                            settings.TWILIO_WHATSAPP_NUMBER)
            otp_service = Twilio_OTPService(sms_service)
            sid = otp_service.send_otp("+"+phone_number.replace('+',''), otp_code)
        return otp_code

    @staticmethod
    def verify_otp(phone_number, otp_code):
        record = OTPRecord.objects.filter(phone_number=phone_number, otp_code=otp_code).last()
        if record and not record.is_expired():
            record.is_verified = True
            record.save()
            return True
        return False
