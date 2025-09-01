from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user','total_price','status','created_at')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass
    

