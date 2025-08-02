from django.db import models
from products.models import Product

# Create your models here.
class AbstractItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    class Meta:
        abstract = True

