from django.contrib.auth.models import AbstractUser
from django.db import models
from utils.g_uuid import GenerateUUID
from django.utils import timezone
from datetime import timedelta
from category.models import Category

class User(AbstractUser):
    USER_ROLES = (
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('bda', 'BDA'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=USER_ROLES)
    email = models.EmailField(unique=True,default=GenerateUUID.generate_random_email)
    username = models.CharField(max_length=150, unique=True, default=GenerateUUID.generate_unique_username)
    phone_number = models.CharField(max_length=15, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)


class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class CustomerProfile(BaseProfile):
    address = models.TextField()

class VendorProfile(BaseProfile):
    shop_name = models.CharField(max_length=255)
    shop_address = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    bda = models.ForeignKey('BDAProfile', null=True, blank=True, on_delete=models.SET_NULL)

class BDAProfile(BaseProfile):
    assigned_area = models.CharField(max_length=255)

class OTPRecord(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at
