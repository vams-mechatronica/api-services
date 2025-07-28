from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(FoodProduct)
class FoodProductAdmin(admin.ModelAdmin):
    list_display = ('name','sku','vendor')
    
