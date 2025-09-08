from django.db import models
from django.contrib.auth import get_user_model
from .common import AbstractItem
from orders.models import Coupon
from decimal import Decimal

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total_price_before_discount(self):
        return sum(item.get_total_price_before_discount() for item in self.items.all())

    def get_total_price_after_discount(self):
        return sum(item.get_total_price_after_discount() for item in self.items.all())

    def get_total_discount(self):
        return self.get_total_price_before_discount() - self.get_total_price_after_discount()

    def get_summary(self):
        return {
            "total_before_discount": self.get_total_price_before_discount(),
            "total_discount": self.get_total_discount(),
            "total_after_discount": self.get_total_price_after_discount(),
        }
    
    def get_total(self):
        total = sum(item.get_total_price_after_discount() for item in self.items.all())
        if self.coupon and self.coupon.active:
            if total >= self.coupon.min_order_amount:
                if self.coupon.discount_type == "percentage":
                    discount = (total * self.coupon.discount_value) / 100
                else:
                    discount = self.coupon.discount_value
                return max(total - discount, 0)
        return total

class CartItem(AbstractItem):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("cart", "product")

    def get_total_price_before_discount(self):
        return self.quantity * self.product.price

    def get_total_price_after_discount(self):
        return self.quantity * self.product.final_price

    def get_total_discount(self):
        return self.get_total_price_before_discount() - self.get_total_price_after_discount()

