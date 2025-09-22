from django.contrib import admin
from .models import DeliveryArea

# Register your models here.
@admin.register(DeliveryArea)
class DeliveryAreaAdmin(admin.ModelAdmin):
    list_display = ('id','pincode','sector','is_active')
    search_fields = ('pincode','sector')
    
