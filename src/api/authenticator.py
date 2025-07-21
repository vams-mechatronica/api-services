from django.contrib.auth import authenticate
from django.core.cache import cache
import random
from accounts.models import *
from django.utils import timezone
from datetime import timedelta
from utils.whatsapp.whatsapp_gateway import WhatsAppGateway
from accounts.services import OTPService

class AuthenticationService:
    OTP_EXPIRY_SECONDS = 300  # 5 minutes

    def send_login_otp(self, phone_number):
        otp = OTPService.generate_otp(phone_number=phone_number)
        cache.set(f'login_otp_{phone_number}', otp, timeout=self.OTP_EXPIRY_SECONDS)
        return otp

    def verify_login_otp(self, phone_number, entered_otp):
        cached_otp = cache.get(f'login_otp_{phone_number}')
        verify = OTPService.verify_otp(phone_number=phone_number,otp_code=entered_otp)
        if verify :
            cache.delete(f'login_otp_{phone_number}')
        return verify

    def password_login(self, username_or_phone, password):
        return authenticate(username=username_or_phone, password=password)
