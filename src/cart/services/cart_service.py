from cart.models import Cart, CartItem
from products.models import Product

def add_or_update_cart_item(cart, product_id, quantity):
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if quantity <= 0:
        cart_item.delete()
    else:
        cart_item.quantity = quantity
        cart_item.price = product.final_price * quantity
        cart_item.save()

    return cart_item
