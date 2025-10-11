from django.contrib.auth import authenticate
from django.core.cache import cache
from accounts.models import *
from accounts.services import OTPService
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()

class AuthenticationService:
    OTP_EXPIRY_SECONDS = 300  # 5 minutes

    def send_login_otp(self, phone_number):
        otp = OTPService.generate_otp(phone_number=phone_number,send_as_sms=False)
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

class UserService:
    def __init__(self, use_jwt=True):
        self.use_jwt = use_jwt  # toggle based on your need

    def get_or_create_user(self, phone_number, role=None):
        user, created = User.objects.get_or_create(phone_number=phone_number, role=role.lower() if role else 'customer')

        if created:
            user.is_phone_verified = True
            user.set_unusable_password()
            user.save()

        return user, created

    def generate_token(self, user):
        if self.use_jwt:
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
        else:
            token, _ = Token.objects.get_or_create(user=user)
            return {
                "token": token.key
            }
