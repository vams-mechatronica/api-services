from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','sku','vendor')

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display = ('name','code','product_type')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product','image','is_primary')
    

    

    
