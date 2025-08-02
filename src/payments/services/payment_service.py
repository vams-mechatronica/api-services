import razorpay, json
from django.conf import settings
from payments.models import Payment
from orders.models import Order
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

def create_razorpay_order(order):
    razorpay_order = client.order.create({
        'amount': int(order.amount * 100),  # in paise
        'currency': 'INR',
        'receipt': f'order_rcptid_{order.id}',
        'payment_capture': 1
    })
    return razorpay_order

def verify_razorpay_signature(payment_id, order_id, signature):
    return client.utility.verify_payment_signature({
        'razorpay_payment_id': payment_id,
        'razorpay_order_id': order_id,
        'razorpay_signature': signature
    })

def initiate_refund(payment_id, amount=None):
    refund_data = {"payment_id": payment_id}
    if amount:
        refund_data["amount"] = int(amount * 100)  # Convert to paisa
    return client.payment.refund(**refund_data)


def refund_payment(payment_id):
    payment = Payment.objects.get(id=payment_id)

    if payment.status != "paid":
        raise Exception("Only paid payments can be refunded")

    refund = client.payment.refund(payment.razorpay_payment_id, {
        "amount": int(payment.amount * 100)
    })

    payment.status = "refunded"
    payment.save()

    return refund

def retry_payment(order_id):
    order = Order.objects.get(id=order_id)
    payment = order.payment

    if payment.status == "paid":
        raise Exception("Payment already completed")

    new_order = client.order.create({
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

def verify_webhook_signature(payload, signature):
    secret = settings.RAZORPAY_WEBHOOK_SECRET
    try:
        razorpay.Utility.verify_webhook_signature(payload, signature, secret)
        return True
    except:
        return False

def process_webhook_payload(payload):
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

def create_wallet_recharge_order(amount, receipt_id):
    return client.order.create({
        'amount': int(amount * 100),  # amount in paise
        'currency': 'INR',
        'receipt': receipt_id,
        'payment_capture': 1
    })

def verify_payment_signature(order_id, payment_id, signature):
    return client.utility.verify_payment_signature({
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    })