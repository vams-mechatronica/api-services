import json
import razorpay
from django.conf import settings
from payments.models import Payment
from orders.models import Order


class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    # ---------- ORDER CREATION ----------
    def create_order_for_purchase(self, order: Order):
        """Create Razorpay order for a product purchase"""
        razorpay_order = self.client.order.create({
            'amount': int(order.amount * 100),  # amount in paise
            'currency': 'INR',
            'receipt': f'order_rcptid_{order.order.id}',
            'payment_capture': 1
        })
        return razorpay_order

    def create_wallet_recharge_order(self, amount: float, receipt_id: str):
        """Create Razorpay order for wallet recharge"""
        return self.client.order.create({
            'amount': int(amount * 100),
            'currency': 'INR',
            'receipt': receipt_id,
            'payment_capture': 1
        })

    def retry_payment(self, order_id: int):
        """Retry payment for an order if not paid"""
        order = Order.objects.get(id=order_id)
        payment = order.payment

        if payment.status == "paid":
            raise Exception("Payment already completed")

        new_order = self.client.order.create({
            "amount": int(order.total_price * 100),
            "currency": "INR",
            "payment_capture": 1,
        })

        payment.razorpay_order_id = new_order['id']
        payment.status = "initiated"
        payment.save()

        return {
            "order_id": new_order['id'],
            "amount": order.total_price,
            "currency": "INR"
        }

    # ---------- SIGNATURE VERIFICATION ----------
    def verify_payment_signature(self, order_id: str, payment_id: str, signature: str):
        """Verify payment signature for checkout"""
        return self.client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

    def verify_webhook_signature(self, payload: str, signature: str):
        """Verify webhook signature"""
        try:
            return self.client.utility.verify_webhook_signature(
                payload, signature, settings.RAZORPAY_WEBHOOK_SECRET
            )
        except Exception:
            return False

    # ---------- REFUND ----------
    def initiate_refund(self, payment_id: str, amount: float = None):
        """Initiate refund (full/partial)"""
        refund_data = {"payment_id": payment_id}
        if amount:
            refund_data["amount"] = int(amount * 100)  # Convert to paise
        return self.client.payment.refund(**refund_data)

    def refund_payment(self, payment_id: int):
        """Refund a payment if paid"""
        payment = Payment.objects.get(id=payment_id)

        if payment.status != "paid":
            raise Exception("Only paid payments can be refunded")

        refund = self.client.payment.refund(payment.razorpay_payment_id, {
            "amount": int(payment.amount * 100)
        })

        payment.status = "refunded"
        payment.save()

        return refund

    # ---------- WEBHOOK PROCESSING ----------
    def process_webhook_payload(self, payload: str):
        """Process Razorpay webhook payload"""
        data = json.loads(payload)
        event = data.get("event")

        if event == "payment.captured":
            payment_id = data["payload"]["payment"]["entity"]["id"]
            try:
                payment = Payment.objects.get(razorpay_payment_id=payment_id)
                payment.status = "paid"
                payment.save()
                payment.order.status = "completed"
                payment.order.save()
            except Payment.DoesNotExist:
                pass
