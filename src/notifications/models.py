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
    to = models.CharField(max_length=20)
    from_number = models.CharField(max_length=20)
    body = models.TextField()
    status = models.CharField(max_length=50, default="queued")
    created_at = models.DateTimeField(default=timezone.now)

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
