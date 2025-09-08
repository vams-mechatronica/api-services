from orders.models import Order, OrderItem, Coupon
from cart.models import Cart, CartItem
from accounts.models import DeliveryAddress

def create_order_from_cart(cart, address_id, payment_method, coupon_code=None):
    address = DeliveryAddress.objects.get(id=address_id)
    coupon = None
    discount = 0

    if coupon_code:
        try:
            coupon = Coupon.objects.get(code=coupon_code, active=True)
            if cart.get_total_price_after_discount() >= coupon.min_order_amount:
                if coupon.discount_type == "percentage":
                    discount = (cart.get_total_price_after_discount() * coupon.discount_value) / 100
                else:
                    discount = coupon.discount_value
        except Coupon.DoesNotExist:
            pass

    order= Order.objects.create(
        user=cart.user,
        address=address,
        payment_method=payment_method,
        coupon=coupon,
        status = 'pending',total_price= 0
    )

    total = 0
    for item in cart.items.all():
        line_total = item.quantity * item.product.final_price
        total += line_total

        # check if order item already exists for this product
        order_item, oi_created = OrderItem.objects.get_or_create(
            order=order,
            product=item.product,
            defaults={
                "quantity": item.quantity,
                "price": item.product.final_price,
            },
        )
        if not oi_created:
            # If it already exists, update the quantity to latest cart value
            order_item.quantity = item.quantity
            order_item.price = item.product.final_price
            order_item.save()

    if discount:
        total = total - discount

    order.total_price = round(total, 2)
    order.save()

    # clear the cart (moved to clear after payment success)
    # cart.items.all().delete()

    return order

