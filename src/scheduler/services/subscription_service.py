# services/subscription_services.py

from wallet.models import Wallet
from scheduler.models import ProductSubscription

def check_wallet_balance_and_update(subscription: ProductSubscription):
    user = subscription.user
    wallet = Wallet.objects.get(user=user)
    
    if wallet.balance >= subscription.total_cost:  # Assuming `amount` is required for renewal
        subscription.eligible_for_delivery = True
    else:
        subscription.eligible_for_delivery = False
        subscription.status = 'paused'
    
    subscription.save()
