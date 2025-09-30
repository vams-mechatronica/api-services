from django.contrib.auth import get_user_model
from category.models import *
from products.models import *
from payments.models import *
from accounts.models import *
from wallet.models import *
from scheduler.models import *
from cart.models import *
from orders.models import *
from personalization.models import *
from delivery.models import DeliveryArea
from notifications.models import WhatsAppMessage, InboundWhatsAppMessage
from rest_framework import serializers
User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password']

    def validate(self, attrs):
        if not attrs.get('email') and not attrs.get('phone_number'):
            raise serializers.ValidationError("Either email or phone number must be provided.")
        return attrs

class CategorySerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Category
        fields = '__all__'
    
    # def get_count(self,obj):
    #     return Product.objects.filter(category__pk=obj.pk).count()


class FoodProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodDetail
        fields = '__all__'
        read_only_fields = ['vendor']

class ElectronicProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicDetail
        fields = '__all__'
        read_only_fields = ['vendor']

class ServiceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceDetail
        fields = '__all__'
        read_only_fields = ['vendor']

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'

class VendorProfileSerializer(serializers.ModelSerializer):
    sub_category_name = serializers.SerializerMethodField()
    class Meta:
        model = VendorProfile
        fields = '__all__'
    
    def get_sub_category_name(self,obj):
        return obj.sub_category.name

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']


class BDAProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BDAProfile
        fields = '__all__'

class BankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetail
        fields = '__all__'

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']

class WalletTransactionSerializer(serializers.ModelSerializer):
    transaction_type = serializers.SerializerMethodField()
    class Meta:
        model = WalletTransaction
        fields = '__all__'
    
    def get_transaction_type(self, obj):
        return obj.get_transaction_type_display()

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    detail = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'vendor', 'category', 'description',
            'price','unit', 'stock', 'image', 'product_type', 'created_at', 'updated_at',
            'images', 'detail'
        ]

    def get_detail(self, obj):
        if obj.product_type == 'food' and hasattr(obj, 'food_detail'):
            return FoodProductSerializer(obj.food_detail).data
        elif obj.product_type == 'electronic' and hasattr(obj, 'electronic_detail'):
            return ElectronicProductSerializer(obj.electronic_detail).data
        elif obj.product_type == 'service' and hasattr(obj, 'service_detail'):
            return ServiceProductSerializer(obj.service_detail).data
        return None


class ProductCreateSerializer(serializers.ModelSerializer):
    food_detail = FoodProductSerializer(required=False)
    electronic_detail = ElectronicProductSerializer(required=False)
    service_detail = ServiceProductSerializer(required=False)

    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'sku', 'vendor', 'category', 'description',
            'price', 'stock', 'image', 'product_type',
            'food_detail', 'electronic_detail', 'service_detail'
        ]

    def create(self, validated_data):
        detail_data = {}
        if 'food_detail' in validated_data:
            detail_data = validated_data.pop('food_detail')
        elif 'electronic_detail' in validated_data:
            detail_data = validated_data.pop('electronic_detail')
        elif 'service_detail' in validated_data:
            detail_data = validated_data.pop('service_detail')

        product = Product.objects.create(**validated_data)

        # Save related detail model
        if product.product_type == 'food':
            FoodDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'electronic':
            ElectronicDetail.objects.create(product=product, **detail_data)
        elif product.product_type == 'service':
            ServiceDetail.objects.create(product=product, **detail_data)

        return product
# serializers.py
class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ['id', 'name', 'code','product_type']


class ProductSimpleSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    unit = UnitSerializer(read_only=True)
    category_name = serializers.SerializerMethodField()
    vendor = VendorProfileSerializer()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
    
    def get_category_name(self,obj):
        return obj.category.name
    
    def get_final_price(self,obj):
        return obj.final_price

class ProductSubscriptionSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ProductSubscription
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_renewed']

class ProductSubscriptionDetailSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = ProductSubscription
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_renewed']

class SimpleProductSubscriptionCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    start_date = serializers.DateField()
    frequency = serializers.ChoiceField(choices=SubscriptionFrequency.choices)
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        from products.models import Product  # Import here to avoid circular import
        try:
            product = Product.objects.get(pk=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found.")
        return value

    def create(self, validated_data):
        from products.models import Product
        user = self.context['request'].user
        product = Product.objects.get(pk=validated_data['product_id'])

        return ProductSubscription.objects.create(
            user=user,
            product=product,
            start_date=validated_data['start_date'],
            frequency=validated_data['frequency'],
            quantity=validated_data['quantity'],
            status='active',
            price=(float(product.price) * float(validated_data['quantity']))
        )

class ProductSummarySerializer(serializers.ModelSerializer):
    unit = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'unit','final_price','discount_type','discount_value','image']
    
    def get_unit(self, obj):
        return obj.unit.code

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSummarySerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), source='product', write_only=True
    )

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    total_price_before_discount = serializers.SerializerMethodField()
    total_price_after_dicount = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total','total_discount','total_price_before_discount','total_price_after_dicount']

    def get_total(self, obj):
        """Calculate cart total based on item quantity * product price"""
        return sum(
            item.quantity * item.product.price 
            for item in obj.items.all()
        )
    
    def get_total_price_before_discount(self, obj):
        return obj.get_total_price_before_discount()
    
    def get_total_price_after_dicount(self, obj):
        return obj.get_total_price_after_discount()
    
    def get_total_discount(self, obj):
        return obj.get_total_discount()

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = '__all__'
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')
        

class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ['id', 'code','discount_type', 'discount_value', 'active']

class VendorCouponSerializer(serializers.ModelSerializer):
    coupon = CouponSerializer()

    class Meta:
        model = VendorCoupon
        fields = ['id', 'vendor', 'coupon', 'valid_from', 'valid_to', 'active']

    def create(self, validated_data):
        coupon_data = validated_data.pop('coupon')
        coupon = Coupon.objects.create(**coupon_data)
        vendor_coupon = VendorCoupon.objects.create(coupon=coupon, **validated_data)
        return vendor_coupon

class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    product_image = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_image', 'quantity', 'price']
    
    def get_product_image(self, obj):
        request = self.context.get("request")
        if obj.product and obj.product.image:
            return request.build_absolute_uri(obj.product.image.url) if request else obj.product.image.url
        return None

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = DeliveryAddressSerializer(read_only=True)
    coupon = CouponSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)

    status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'coupon', 'address', 'payment_method','payment', 'status', 'created_at', 'items']
    
    def get_status(self, obj):
        return obj.get_status_display()

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.IntegerField()
    address_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)
    coupon_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

class AddCartItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid product_id: Product does not exist.")
        return value

class TermsAndConditionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAndConditions
        fields = '__all__'

class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class ShopAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopAddress
        fields = '__all__'


class ShopDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopDocument
        fields = '__all__'

class ShopDocumentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopDocumentFile
        fields = ['id', 'shop_doc', 'name', 'file', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'role', 'is_phone_verified', 'is_email_verified']



class BDASerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = BDAProfile
        fields = ['id', 'region', 'user']


class VendorDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    sub_category = CategorySerializer()
    bda = BDASerializer()
    bank_details = BankDetailSerializer(many=True)
    shop_location = ShopAddressSerializer()
    documents = ShopDocumentSerializer(many=True)

    class Meta:
        model = VendorProfile
        fields = [
            'id',
            'user',
            'shop_name',
            'shop_address',
            'category',
            'sub_category',
            'bda',
            'trial_ends_at',
            'bank_details',
            'shop_location',
            'documents',
            'is_in_trial',
        ]

class UserSerializerDetail(serializers.ModelSerializer):
    customerprofile = CustomerProfileSerializer(read_only=True)
    vendorprofile = VendorProfileSerializer(read_only=True)
    bdaprofile = BDAProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 'role',
            'is_phone_verified', 'is_email_verified',
            'customerprofile', 'vendorprofile', 'bdaprofile'
        ]


class DeliveryAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryArea
        fields = ['id', 'pincode', 'sector', 'is_active']


class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = "__all__"


class InboundWhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InboundWhatsAppMessage
        fields = "__all__"