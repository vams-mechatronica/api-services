from .base import BaseObserver
from notifications.models import OutboxEvent
from notifications.services import enqueue_message

class EmailObserver(BaseObserver):
    def update(self, **kwargs):
        payment = kwargs.get("payment")
        order = kwargs.get("order")
        user = kwargs.get("user")

        enqueue_message(recipient='info@vamsmechatronica.in',
                subject="Order Created",
                body=f"order #{order.id} has been created successfully.",
                channel='email')

        # OutboxEvent.objects.create(
        #     event_type="EmailNotification",
        #     payload={
        #         "recipient": user.email,
        #         "subject": f"Payment Confirmed - Order #{order.id}",
        #         "body": f"Your payment of ₹{order.total_amount} for order #{order.id} is successful.",
        #     },
        # )
