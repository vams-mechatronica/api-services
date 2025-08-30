from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    pass

@admin.register(WalletTransaction)
class WalletTransactionAdmin(admin.ModelAdmin):
    pass
    
@admin.register(WalletRecharge)
class WalletRechargeAdmin(admin.ModelAdmin):
    pass
    


    
