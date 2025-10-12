# payments/observers/wallet_observer.py
from .base import BaseObserver
from wallet.models import Wallet

class WalletObserver(BaseObserver):
    def update(self, **kwargs):
        payment = kwargs.get("payment")
        order = kwargs.get("order")
        user = kwargs.get("user")

        # Deduct from user wallet
        try:
            wallet = Wallet.objects.get(user=user)
            wallet.balance -= order.total_amount
            wallet.save()
        except Wallet.DoesNotExist:
            pass

        # Credit vendor wallet
        if hasattr(order, "vendor"):
            try:
                vendor_wallet = Wallet.objects.get(user=order.vendor)
                vendor_wallet.balance += order.total_amount
                vendor_wallet.save()
            except Wallet.DoesNotExist:
                pass
