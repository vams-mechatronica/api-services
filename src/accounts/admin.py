from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('role','email','username','phone_number','is_phone_verified','is_email_verified')

@admin.register(BDAProfile)
class BDAProfileAdmin(admin.ModelAdmin):
    list_display = ('id','region')

@admin.register(OTPRecord)
class OTPRecordAdmin(admin.ModelAdmin):
    list_display = ('phone_number','otp_code','is_verified','is_expired')
    

@admin.register(BankDetail)
class BankDetailAdmin(admin.ModelAdmin):
    list_display = ('id','profile','content_type','object_id')

@admin.register(VendorProfile)
class VendorProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name','get_phone_number','category','sub_category','bda','trial_ends_at','created_at','updated_at')

@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(ShopAddress)
class ShopAddressAdmin(admin.ModelAdmin):
    list_display = ('id','vendor','created_at','updated_at')

@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user','address_line','city','created_at')
    

    

    

    

    

