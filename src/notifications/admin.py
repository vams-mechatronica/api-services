from django.contrib import admin
from .models import *


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    pass

@admin.register(MessageQueue)
class MessageQueueAdmin(admin.ModelAdmin):
    list_display = ('subject','is_sent','created_at','sent_at')

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    pass

@admin.register(InboundWhatsAppMessage)
class InboundWhatsAppMessageAdmin(admin.ModelAdmin):
    pass
    
@admin.register(EmailSentLog)
class EmailSentLogAdmin(admin.ModelAdmin):
    pass

@admin.register(EmailMarketingLog)
class EmailMarketingLogAdmin(admin.ModelAdmin):
    pass


    

    

@admin.register(MarketingCampaign)
class MarketingCampaignAdmin(admin.ModelAdmin):
    list_display = ('template_id','template_name','created_at')

@admin.register(MarketingContact)
class MarketingContactAdmin(admin.ModelAdmin):
    list_display = ('phone_number','name','email','active')
    search_fields = ('phone_number','name','email')

@admin.register(MarketingLog)
class MarketingLogAdmin(admin.ModelAdmin):
    pass
    

    


