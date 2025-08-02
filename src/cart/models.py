from django.db import models
from django.contrib.auth import get_user_model
from .common import AbstractItem

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(AbstractItem):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')

    class Meta:
        unique_together = ('cart', 'product')
