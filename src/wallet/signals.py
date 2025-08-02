from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Wallet

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        # Assuming Vendor has a profile flag
        is_vendor = hasattr(instance, 'vendorprofile')
        Wallet.objects.create(user=instance, is_vendor=is_vendor)
