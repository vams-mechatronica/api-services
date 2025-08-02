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
            discount = coupon.discount_percent
        except Coupon.DoesNotExist:
            pass

    order = Order.objects.create(
        user=cart.user,
        address=address,
        payment_method=payment_method,
        coupon=coupon,
        total_price=0
    )

    total = 0
    for item in cart.items.all():
        line_total = item.quantity * item.product.price
        total += line_total
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    if discount:
        total = total * (1 - discount / 100.0)

    order.total_price = round(total, 2)
    order.save()
    cart.items.all().delete()  # Clear cart after ordering
    return order
