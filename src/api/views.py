from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.services import OTPService
user = get_user_model()

class RequestSignupOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_service = OTPService()
        otp_service.generate_otp(phone_number)

        return Response({'message': 'OTP sent to WhatsApp.'}, status=status.HTTP_200_OK)


class VerifySignupOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        name = request.data.get('name')  # Optional during OTP verification

        if not phone_number or not otp:
            return Response({'error': 'Phone number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_service = OTPService()
        if otp_service.verify_otp(phone_number, otp):
            cuser, created = user.objects.get_or_create(phone_number=phone_number)
            if name and created:
                cuser.phone_number = phone_number  # or generate a username
                cuser.set_unusable_password()
                cuser.save()

            return Response({'message': 'Signup successful.', 'user_id': cuser.id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)
