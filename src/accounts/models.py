from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from utils.g_uuid import GenerateUUID
from django.utils import timezone
from datetime import timedelta
from category.models import Category
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation

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

# Create your models here.
class BankDetail(models.Model):
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    upi_id = models.CharField(max_length=100, blank=True, null=True)

    # Generic relation to link with any profile model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    profile = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BaseProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True

class CustomerProfile(BaseProfile):
    address = models.TextField()
    bank_details = GenericRelation(BankDetail)

class VendorProfile(BaseProfile):
    shop_name = models.CharField(max_length=255)
    shop_address = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    bda = models.ForeignKey('BDAProfile', null=True, blank=True, on_delete=models.SET_NULL)
    trial_ends_at = models.DateField(null=True, blank=True)
    bank_details = GenericRelation(BankDetail)

    def is_in_trial(self):
        return self.trial_ends_at and timezone.now().date() <= self.trial_ends_at

class BDAProfile(BaseProfile):
    region = models.CharField(max_length=255)
    bank_details = GenericRelation(BankDetail)


class OTPRecord(models.Model):
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.expires_at

class DeliveryAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address_line = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)


