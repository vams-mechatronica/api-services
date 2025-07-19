from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db import models

from abc import ABC,abstractmethod

class EmailOrPhoneBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(
                models.Q(email=username) | models.Q(phone_number=username)
            )
        except UserModel.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None

class AuthenticationStrategy(ABC):
    @abstractmethod
    def authenticate(self, request):
        pass
