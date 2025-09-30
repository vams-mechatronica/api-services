from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class MessageTemplate(models.Model):
    class Channel(models.TextChoices):
        EMAIL = 'email', _('Email')
        SMS = 'sms', _('SMS')
        WHATSAPP = 'whatsapp', _('WhatsApp')
        PUSH = 'push', _('Push Notification')

    name = models.CharField(
        max_length=150,
        unique=True,
        help_text="Internal name/key for the template, e.g. 'welcome_email'"
    )
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        help_text="Where this template is used"
    )
    subject = models.CharField(
        max_length=255,
        blank=True,
        help_text="Subject for email or title for push. Leave blank for SMS/WhatsApp."
    )
    body = models.TextField(
        help_text="Body text. You can use {{ placeholders }} for dynamic values."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'channel')
        ordering = ['name']

    def __str__(self):
        return f"{self.get_channel_display()}: {self.name}"


class MessageQueue(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    channel = models.CharField(max_length=50, default='email')  # 'email','sms', etc.
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient}: {self.channel} - sent: {self.is_sent}"

class WhatsAppMessage(models.Model):
    """
    Stores outbound messages sent via Twilio WhatsApp
    """
    SID = models.CharField(max_length=100, unique=True, help_text="Twilio Message SID")
    account_sid = models.CharField(max_length=100, blank=True, null=True)
    messaging_service_sid = models.CharField(max_length=100, blank=True, null=True)
    to = models.CharField(max_length=20, blank=True, null=True)
    from_number = models.CharField(max_length=20, blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default="queued")  # queued, sent, delivered, failed, read
    error_code = models.CharField(max_length=50, blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    num_segments = models.IntegerField(default=1)
    api_version = models.CharField(max_length=20, blank=True, null=True)
    price = models.CharField(max_length=20, blank=True, null=True)
    price_unit = models.CharField(max_length=10, blank=True, null=True)
    direction = models.CharField(max_length=20, blank=True, null=True)  # inbound/outbound
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.to} - {self.status}"

class InboundWhatsAppMessage(models.Model):
    """
    Stores inbound (user reply) messages from WhatsApp
    """
    SID = models.CharField(max_length=100, unique=True, help_text="Twilio Message SID")
    from_number = models.CharField(max_length=20)
    to = models.CharField(max_length=20)
    body = models.TextField()
    received_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"From {self.from_number} - {self.body[:30]}"

class MarketingContact(models.Model):
    """
    Stores phone numbers for campaign targets
    """
    phone_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.phone_number} ({'Active' if self.active else 'Inactive'})"


class MarketingCampaign(models.Model):
    """
    Campaign info (title, message, etc.)
    """
    template_id = models.CharField(_("template_id"), max_length=255)
    template_name = models.CharField(_("template_name"), max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.template_name


class MarketingLog(models.Model):
    """
    Log of messages sent to each contact
    """
    contact = models.ForeignKey(MarketingContact, on_delete=models.CASCADE)
    campaign = models.ForeignKey(MarketingCampaign, on_delete=models.CASCADE)
    sent = models.BooleanField(default=False)
    iteration_count = models.IntegerField(default=0)
    last_sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("contact", "campaign")

    def __str__(self):
        return f"{self.contact.phone_number} - {self.campaign.template_name} - Iter {self.iteration_count}"
