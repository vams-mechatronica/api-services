# models/wallet.py
from datetime import timedelta
from django.db import models
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth import get_user_model
user = get_user_model()

class Wallet(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    last_deducted_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Wallet: {self.user.username}"

    def add_funds(self, amount):
        self.balance += Decimal(amount)
        self.save()

    def deduct_funds(self, amount):
        if self.balance >= Decimal(amount):
            self.balance -= Decimal(amount)
            self.save()
            return True
        return False
    

    def is_vendor_wallet(self):
        return hasattr(self.user, 'vendorprofile')

    def get_subscription_plan(self):
        if self.is_vendor_wallet():
            return self.user.vendorprofile.category.categorysubscriptionplan
        return None

    def should_charge_today(self):
        if not self.is_vendor_wallet():
            return False  # Not applicable

        today = timezone.now().date()
        plan = self.get_subscription_plan()

        if not self.last_deducted_on:
            return True  # Never charged

        if plan.frequency == 'daily':
            return self.last_deducted_on < today
        elif plan.frequency == 'weekly':
            return self.last_deducted_on <= today - timedelta(weeks=1)
        elif plan.frequency == 'monthly':
            return self.last_deducted_on <= today - relativedelta(months=1)
        return False

    def charge_subscription(self):
        if not self.should_charge_today():
            return True

        plan = self.get_subscription_plan()
        if self.balance >= plan.cost:
            self.balance -= plan.cost
            self.last_deducted_on = timezone.now().date()
            self.save()
            WalletTransaction.objects.create(
                wallet=self,
                amount=plan.cost,
                transaction_type='DEBIT',
                description=f"{plan.frequency.title()} vendor subscription"
            )
            return True
        return False


class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('credit', 'Credit'),
        ('debit', 'Debit'),
        ('upi', 'UPI'),
        ('net-banking', 'Net Banking'),
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.transaction_type.title()} of ₹{self.amount} on {self.timestamp.date()}"

class WalletRecharge(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='recharges')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.TextField(null=True, blank=True)
    
    STATUS_CHOICES = (
        ('created', 'Created'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def mark_successful(self, payment_id, signature):
        self.razorpay_payment_id = payment_id
        self.razorpay_signature = signature
        self.status = 'success'
        self.completed_at = timezone.now()
        self.save()
