from django.db import models
from cart.common import AbstractItem
from accounts.models import DeliveryAddress
from django.contrib.auth import get_user_model
from accounts.models import VendorProfile

User = get_user_model()

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)


class VendorCoupon(models.Model):
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE, related_name='vendor_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='vendor_coupons')
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('vendor', 'coupon')  # Optional

    def __str__(self):
        return f"{self.vendor.shop_name} - {self.coupon.code}"




class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cod', 'Cash On Delivery'),
        ('razorpay', 'Razorpay'),
        ('upi', 'UPI'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(AbstractItem):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
