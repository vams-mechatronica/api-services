from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(ProductSubscription)
class ProductSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'start_date', 'frequency', 'quantity', 'status', 'created_at', 'updated_at', 'last_renewed')