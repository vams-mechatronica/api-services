from django.contrib import admin
from .models import *


# Register your models here.
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title','position','is_active')
    
