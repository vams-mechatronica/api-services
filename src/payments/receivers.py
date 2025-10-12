from django.dispatch import receiver
from .signals import payment_completed
from .dispatcher import EventDispatcher
from .observers.email_observer import EmailObserver
from .observers.wallet_observer import WalletObserver
from .observers.analytics_observer import AnalyticsObserver
from .observers.vendor_order_observer import VendorOrderObserver

# Register all observers for PaymentCompleted
EventDispatcher.register("PaymentCompleted", EmailObserver())
EventDispatcher.register("PaymentCompleted", AnalyticsObserver())
EventDispatcher.register("PaymentCompleted", VendorOrderObserver())

@receiver(payment_completed)
def handle_payment_completed(sender, **kwargs):
    EventDispatcher.notify("PaymentCompleted", **kwargs)
