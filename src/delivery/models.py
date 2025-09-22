# delivery/models.py
from django.db import models

class DeliveryArea(models.Model):
    pincode = models.CharField(max_length=10)
    sector = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('pincode', 'sector')

    def __str__(self):
        return f"{self.sector} - {self.pincode}"
