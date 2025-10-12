# payments/observers/analytics_observer.py
from .base import BaseObserver
from analytics.models import EventLog

class AnalyticsObserver(BaseObserver):
    def update(self, **kwargs):
        order = kwargs.get("order")
        payment = kwargs.get("payment")

        EventLog.objects.create(
            event_type="PaymentCompleted",
            reference_id=str(payment.id),
            metadata={"order_id": order.id, "amount": float(order.total_price)},
        )
