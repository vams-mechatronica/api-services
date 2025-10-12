# orders/observers/vendor_order_observer.py
from .base import BaseObserver
from vendors.vendors_orders.models import VendorOrder, VendorOrderItem

class VendorOrderObserver(BaseObserver):
    """
    Observer that creates vendor-side orders whenever a user order is created or paid.
    """

    def update(self, **kwargs):
        order = kwargs.get("order")
        if not order:
            return

        # Group order items by vendor
        vendor_items_map = {}
        for item in order.items.all():
            vendor = item.product.vendor
            if vendor not in vendor_items_map:
                vendor_items_map[vendor] = []
            vendor_items_map[vendor].append(item)

        # Create VendorOrders for each vendor
        for vendor, items in vendor_items_map.items():
            total_amount = sum([item.price * item.quantity for item in items])
            vendor_order = VendorOrder.objects.create(
                vendor=vendor,
                external_id=order.id,
                customer_name=order.user.username,
                customer_phone=order.user.phone_number,
                customer_address=order.address.get_full_address(),
                total_amount=total_amount,
                status="pending",
                is_paid= True if order.status == 'completed' else False
            )

            # Add items to VendorOrder
            for item in items:
                VendorOrderItem.objects.create(
                    order=vendor_order,
                    product=item.product,
                    product_snapshot = {"name":item.product.name},
                    quantity=item.quantity,
                    unit_price=item.price
                )
