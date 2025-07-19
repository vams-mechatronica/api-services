from django.urls import path,include
from .views import *

urlpatterns = [
    path('generate-otp',RequestSignupOTP.as_view()),
    path('verify-otp',VerifySignupOTP.as_view())
]
