from django.db import models
from django.conf import settings
from products.models import Product
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
User = get_user_model()
from datetime import timedelta
from django.utils import timezone

class SubscriptionFrequency(models.TextChoices):
    DAILY = "daily", _("Daily")
    ALTERNATE_DAY = "alternate_day", _("Alternate Day")
    EVERY_3_DAYS = "every_3_days", _("Every 3 Days")
    WEEKLY = "weekly", _("Weekly")
    BI_WEEKLY = "biweekly", _("Bi-Weekly")
    MONTHLY = "monthly", _("Monthly")
    YEARLY = "yearly", _("Yearly")

class SubscriptionStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    CANCELLED = "cancelled", _("Cancelled")
    PAUSED = "paused", _("Paused")
    EXPIRED = "expired", _("Expired")

class ProductSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='product_subscriptions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='subscriptions')

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    frequency = models.CharField(max_length=20, choices=SubscriptionFrequency.choices, default=SubscriptionFrequency.DAILY)
    status = models.CharField(max_length=10, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE)

    last_renewed = models.DateField(auto_now_add=True)
    next_renewal_date = models.DateField(null=True, blank=True)

    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0.0)

    remarks = models.TextField(_("Remarks"), blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    eligible_for_delivery = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.product} ({self.frequency})"

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    @property
    def total_cost(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        # If end_date is not set, make it 1 year from start_date
        if not self.end_date:
            base_date = self.start_date or timezone.now().date()
            self.end_date = base_date + timedelta(days=365)
        super().save(*args, **kwargs)
