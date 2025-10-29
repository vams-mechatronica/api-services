from django.contrib import admin
from .models import *


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ('name','channel','is_active','created_at','updated_at')
    search_fields = ('name','channel')
    sortable_by = ('name','channel','is_active')

@admin.register(MessageQueue)
class MessageQueueAdmin(admin.ModelAdmin):
    list_display = ('recipient','subject','channel','is_sent','created_at','sent_at')
    search_fields = ('recipient','subject','channel')

@admin.register(WhatsAppMessage)
class WhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('to','from_number','status','created_at','updated_at')
    search_fields = ('to','status')

@admin.register(InboundWhatsAppMessage)
class InboundWhatsAppMessageAdmin(admin.ModelAdmin):
    list_display = ('from_number','to','body','received_at')
    search_fields = ('from_number','to','body','received_at')
    
@admin.register(EmailSentLog)
class EmailSentLogAdmin(admin.ModelAdmin):
    list_display = ('start_index','end_index','created_at','updated_at')
    sortable_by = ('start_index','end_index','created_at','updated_at')

@admin.register(EmailMarketingLog)
class EmailMarketingLogAdmin(admin.ModelAdmin):
    list_display = ('contact','template','sent','iteration_count','last_sent_at')
    search_fields = ('contact','template')
    sortable_by = ('last_sent_at')


    

    

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
    

    


