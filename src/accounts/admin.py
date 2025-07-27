from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('role','email','username','phone_number','is_phone_verified','is_email_verified')

@admin.register(BDAProfile)
class BDAProfileAdmin(admin.ModelAdmin):
    list_display = ('id','region')
    
