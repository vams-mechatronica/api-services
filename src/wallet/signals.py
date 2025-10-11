from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Wallet
User = get_user_model()

@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        initial_balance = 2000 if getattr(instance, 'role', '') == 'vendor' else 0
        Wallet.objects.create(user=instance, balance=initial_balance)
