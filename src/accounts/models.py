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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class CustomerProfile(BaseProfile):
    address = models.TextField()
    bank_details = GenericRelation(BankDetail)

class VendorProfile(BaseProfile):
    PRODUCT_TYPES = (
        ('food', 'Food'),
        ('electronic', 'Electronic'),
        ('service', 'Service'),
        # Add more as needed
    )
    shop_name = models.CharField(max_length=255)
    shop_address = models.TextField()
    category = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='food')
    sub_category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    bda = models.ForeignKey('BDAProfile', null=True, blank=True, on_delete=models.SET_NULL)
    trial_ends_at = models.DateField(null=True, blank=True)
    bank_details = GenericRelation(BankDetail)

    def is_in_trial(self):
        return self.trial_ends_at and timezone.now().date() <= self.trial_ends_at
    
    def get_phone_number(self):
        return self.user.phone_number

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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ShopAddress(models.Model):
    vendor = models.OneToOneField(VendorProfile, on_delete=models.CASCADE, related_name='shop_location')
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=64)
    state = models.CharField(max_length=64)
    country = models.CharField(max_length=64)
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    longitude = models.DecimalField(max_digits=20, decimal_places=15, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.shop_name} - {self.city}"


class ShopDocument(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='documents')
    registration_number = models.CharField(max_length=50, blank=True)
    gstin = models.CharField(max_length=15, blank=True)
    pan_card = models.CharField(max_length=10, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vendor.shop_name} - Documents"

class ShopDocumentFile(models.Model):
    shop_doc = models.ForeignKey(ShopDocument, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='shop_docs/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "ShopDocumentFile"
        verbose_name_plural = "ShopDocumentFiles"

    def __str__(self):
        return self.name

