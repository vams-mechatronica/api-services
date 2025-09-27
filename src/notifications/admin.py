from django.contrib import admin
from .models import *


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    pass

@admin.register(MessageQueue)
class MessageQueueAdmin(admin.ModelAdmin):
    list_display = ('subject','is_sent','created_at','sent_at')
    

    
