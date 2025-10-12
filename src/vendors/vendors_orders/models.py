from django.db import models
from accounts.models import VendorProfile
from products.models import Product

# Create your models here.
class VendorOrder(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=200, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True)
    customer_phone = models.CharField(max_length=50, blank=True)
    customer_address = models.JSONField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class VendorOrderItem(models.Model):
    order = models.ForeignKey(VendorOrder, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_snapshot = models.JSONField()
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, default=0.0)

class VendorOrderPayment(models.Model):
    order = models.ForeignKey(VendorOrder, on_delete=models.SET_NULL, null=True)
    provider = models.CharField(max_length=50)
    provider_payment_id = models.CharField(max_length=200, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class VendorOrderStatusHistory(models.Model):
    order = models.ForeignKey(VendorOrder, on_delete=models.CASCADE, related_name='history')
    from_status = models.CharField(max_length=50, blank=True, null=True)
    to_status = models.CharField(max_length=50)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)