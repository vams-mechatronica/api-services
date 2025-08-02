from django.db import models
from orders.models import Order


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="INR")

    payment_gateway = models.CharField(max_length=20, choices=[("razorpay", "Razorpay"), ("stripe", "Stripe")])
    status = models.CharField(max_length=20, choices=[
        ("initiated", "Initiated"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded")
    ], default="initiated")

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

