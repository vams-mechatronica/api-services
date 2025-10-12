import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import JSONField

User = get_user_model()

class EventLog(models.Model):
    """
    Stores immutable log of system events (payments, orders, wallet updates, etc.)
    Used for analytics, debugging, or auditing.
    """

    EVENT_CHOICES = [
        ("PaymentCompleted", "Payment Completed"),
        ("OrderCreated", "Order Created"),
        ("WalletUpdated", "Wallet Updated"),
        ("DeliveryCompleted", "Delivery Completed"),
        ("RefundProcessed", "Refund Processed"),
        ("NotificationSent", "Notification Sent"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=64, choices=EVENT_CHOICES)
    reference_id = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="ID of related object (Order/Payment/Wallet)."
    )
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="event_logs"
    )
    metadata = JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    class Meta:
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["created_at"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.event_type} ({self.reference_id or 'NoRef'})"

    @classmethod
    def log(cls, event_type, reference_id=None, user=None, metadata=None):
        """Convenience method for creating a log entry."""
        return cls.objects.create(
            event_type=event_type,
            reference_id=reference_id,
            user=user,
            metadata=metadata or {},
        )
