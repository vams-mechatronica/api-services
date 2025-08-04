from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.services import OTPService
from .authenticator import AuthenticationService, UserService
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from .permissions import *
from .serializers import *
from datetime import date
user = get_user_model()
import hmac, hashlib, json
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from cart.services.cart_service import add_or_update_cart_item
from orders.services.order_service import create_order_from_cart
from payments.services.payment_service import create_razorpay_order,verify_razorpay_signature,verify_webhook_signature, process_webhook_payload, create_wallet_recharge_order, verify_payment_signature
from scheduler.services.subscription_service import check_wallet_balance_and_update

class RequestSignupOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_service = OTPService()
        otp_service.generate_otp(phone_number)

        return Response({'message': 'OTP sent to WhatsApp.'}, status=status.HTTP_200_OK)


class VerifySignupOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        role = request.data.get('role')

        if not phone_number or not otp:
            return Response({'error': 'Phone number and OTP are required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_service = OTPService()
        if otp_service.verify_otp(phone_number, otp):
            user_service = UserService(use_jwt=True)  # or False for Django Token
            cuser, created = user_service.get_or_create_user(phone_number, role)
            token = user_service.generate_token(cuser)

            return Response({
                'message': 'Signup successful.',
                'user_id': cuser.id,
                'token': token
            }, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)




class RequestLoginOTP(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number required.'}, status=status.HTTP_400_BAD_REQUEST)

        auth_service = AuthenticationService()
        auth_service.send_login_otp(phone_number)

        return Response({'message': 'OTP sent via WhatsApp.'})


class VerifyLoginOTP(APIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')
        role = request.data.get('role')
        bdaUserId = None
        if not phone_number or not otp:
            return Response({'error': 'Phone number and OTP required.'}, status=status.HTTP_400_BAD_REQUEST)

        auth_service = AuthenticationService()
        if auth_service.verify_login_otp(phone_number, otp):
            user_service = UserService(use_jwt=True)  # or False for Django Token
            cuser, created = user_service.get_or_create_user(phone_number.replace('+',''))
            token = user_service.generate_token(cuser)
            if not cuser:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            if role and role == 'bda':
                bdaObj = get_object_or_404(BDAProfile,user=cuser)
                if bdaObj:
                    bdaUserId = bdaObj.pk
            return Response({'message': 'Login successful.', 'user_id': cuser.id,'bdaUserId':bdaUserId, 'token':token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordLogin(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        if not identifier or not password:
            return Response({'error': 'Identifier and password required.'}, status=status.HTTP_400_BAD_REQUEST)

        auth_service = AuthenticationService()
        user = auth_service.password_login(identifier, password)

        if user:
            return Response({'message': 'Login successful.', 'user_id': user.id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

# Category & Sub-Category

# GET: List, POST: Create (Admin/BDA only)
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication,SessionAuthentication)

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated(), IsAdminOrBDA()]
        return [permissions.AllowAny()]


# GET: Retrieve, PUT/PATCH: Update, DELETE (Admin/BDA only)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = (BasicAuthentication, TokenAuthentication,SessionAuthentication)


    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAdminOrBDA()]
        return [permissions.AllowAny()]


# Products 

###### Food Products

# GET (List) + POST (Create)
class FoodProductListCreateView(generics.ListCreateAPIView):
    serializer_class = FoodProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = (BasicAuthentication, TokenAuthentication,SessionAuthentication)

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category', 'is_service', 'vendor']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'name', 'stock_quantity']

    def get_queryset(self):
        vendor = VendorProfile.objects.get(user=self.request.user)
        return FoodDetail.objects.filter(vendor=vendor)

    def perform_create(self, serializer):
        vendor = VendorProfile.objects.get(user=self.request.user)
        if vendor.category.name.lower() != "restaurant":
            raise PermissionDenied("Only Restaurant vendors can add food products.")
        serializer.save(vendor=vendor)

# GET, PUT, PATCH, DELETE
class FoodProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodDetail.objects.all()
    serializer_class = FoodProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsVendorOrReadOnly]
    authentication_classes = (BasicAuthentication, TokenAuthentication,SessionAuthentication)


# --- Customer Profile CRUD ---
class CustomerProfileListCreateView(generics.ListCreateAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer


class CustomerProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer


# --- Vendor Profile CRUD ---
class VendorProfileListCreateView(generics.ListCreateAPIView):
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ('shop_name',)
    filterset_fields = ('category',)
    permission_classes = (AllowAny,)
    queryset = VendorProfile.objects.all()
    serializer_class = VendorProfileSerializer


class VendorProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (AllowAny,)
    queryset = VendorProfile.objects.all()
    serializer_class = VendorDetailSerializer


# --- BDA Profile CRUD ---
class BDAProfileListCreateView(generics.ListCreateAPIView):
    queryset = BDAProfile.objects.all()
    serializer_class = BDAProfileSerializer


class BDAProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BDAProfile.objects.all()
    serializer_class = BDAProfileSerializer


# --- Bank Detail CRUD ---
class BankDetailListCreateView(generics.ListCreateAPIView):
    queryset = BankDetail.objects.all()
    serializer_class = BankDetailSerializer


class BankDetailDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = BankDetail.objects.all()
    serializer_class = BankDetailSerializer

class VendorProductsListView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = FoodProductSerializer

    def get_queryset(self):
        vendor_id = self.request.GET.get('vendor_id')
        if not vendor_id:
            return FoodDetail.objects.none()
        return FoodDetail.objects.filter(product__vendor_id=vendor_id)

    def list(self, request, *args, **kwargs):
        vendor_id = self.request.GET.get('vendor_id')
        if not vendor_id:
            return Response({'message': 'vendor_id is compulsory'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        return Response(WalletSerializer(wallet).data)

class RechargeWalletAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication)
    
    def post(self,request,*args, **kwargs):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount required"}, status=400)
        
        wallet = Wallet.objects.get(user=request.user)
        wallet.add_funds(amount)
        WalletTransaction.objects.create(wallet=wallet, amount=amount, transaction_type='credit', description="Wallet recharge")
        
        return Response({"message": "Recharge successful", "balance": wallet.balance})

# views.py
class InitiateWalletRechargeAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = float(request.data.get('amount'))
        if not amount or amount <= 0:
            return Response({"error": "Valid amount required"}, status=400)

        wallet = Wallet.objects.get(user=request.user)
        receipt_id = f"wallet_recharge_{request.user.id}_{timezone.now().timestamp()}"
        order = create_wallet_recharge_order(amount, receipt_id)

        WalletRecharge.objects.create(
            wallet=wallet,
            amount=amount,
            razorpay_order_id=order['id']
        )

        return Response({
            "order_id": order['id'],
            "amount": amount,
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

class VerifyWalletRechargeAPI(APIView):
    permission_classes = [AllowAny]  # Or secure it via Razorpay webhook signature

    def post(self, request):
        data = request.data
        try:
            verify_payment_signature(
                data['razorpay_order_id'],
                data['razorpay_payment_id'],
                data['razorpay_signature']
            )

            recharge = WalletRecharge.objects.get(razorpay_order_id=data['razorpay_order_id'])
            if recharge.status != 'success':
                recharge.status = 'success'
                recharge.razorpay_payment_id = data['razorpay_payment_id']
                recharge.save()

                # Update wallet
                wallet = recharge.wallet
                wallet.add_funds(recharge.amount)
                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=recharge.amount,
                    transaction_type='credit',
                    description='Razorpay Wallet Recharge'
                )

            return Response({'status': 'success'})

        except Exception as e:
            return Response({'error': str(e)}, status=400)


class VendorDailyAccessAPI(APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)
    def post(self, request, *args, **kwargs):
        wallet = Wallet.objects.get(user=request.user)
        if not wallet.is_vendor:
            return Response({"error": "Not a vendor"}, status=403)

        today = date.today()
        already_deducted = WalletTransaction.objects.filter(wallet=wallet, description=f"Access fee for {today}").exists()
        if already_deducted:
            return Response({"message": "Today's access already granted."})

        if wallet.deduct_funds(10):  # Example: ₹10 per day
            WalletTransaction.objects.create(wallet=wallet, amount=10, transaction_type='debit', description=f"Access fee for {today}")
            return Response({"message": "Access granted for today."})
        else:
            return Response({"error": "Insufficient balance."}, status=402)


class ProductListView(generics.ListAPIView):
    authentication_classes = (TokenAuthentication, )
    permission_classes = (AllowAny,)
    serializer_class = ProductSimpleSerializer
    queryset = Product.objects.all().select_related('category', 'vendor').prefetch_related('images')

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['category','category__slug']  # or use 'category__id' if FK id isn't working directly
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'updated_at', 'stock']
    ordering = ['-created_at']  # default order

class ProductSubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['frequency', 'status', 'product']

    def get_queryset(self):
        subscriptions = ProductSubscription.objects.filter(user=self.request.user)
        for sub in subscriptions:
            check_wallet_balance_and_update(sub)
        return subscriptions

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Retrieve, Update, Delete
class ProductSubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ProductSubscription.objects.filter(user=self.request.user.id)

class CreateSimpleProductSubscriptionView(generics.GenericAPIView):
    serializer_class = SimpleProductSubscriptionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()
        return Response({
            "message": "Subscription created successfully.",
            "subscription_id": subscription.id
        }, status=status.HTTP_201_CREATED)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = add_or_update_cart_item(cart, product_id, quantity)

        return Response({'message': 'Item updated successfully'}, status=status.HTTP_200_OK)


class CartView(generics.RetrieveAPIView):
    """
    Retrieve the current authenticated user's cart.

    This view returns the cart and its associated items for the user making the request.
    If the cart does not exist, a new one is created automatically.

    Authentication:
        - BasicAuthentication
        - TokenAuthentication
        - SessionAuthentication

    Permissions:
        - User must be authenticated
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication)
    serializer_class = CartSerializer

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddCartItemView(APIView):
    """This api will be used to add or remove cart items. To remove cart items just pass quantity as 0"""
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication)

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = add_or_update_cart_item(cart, product_id, quantity)

        return Response({'message': 'Item updated successfully'}, status=200)

class OrderListView(generics.ListAPIView):
    """
    List all orders placed by the authenticated user.

    Returns a list of orders associated with the currently authenticated user,
    including order details such as items, totals, payment status, and delivery information.

    Permissions:
        - User must be authenticated
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class CreateOrderView(APIView):
    """
    Create a new order from a user's cart.

    This view:
    - Accepts `cart_id`, `address_id`, `payment_method`, and optional `coupon_code`.
    - Validates the input using `CreateOrderSerializer`.
    - Converts the cart into an order and calculates total, discounts, and payment details.

    Returns:
        - Created order data if successful.
        - Error response if the process fails.

    Permissions:
        - User must be authenticated
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication)


    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart_id = serializer.validated_data['cart_id']
        address_id = serializer.validated_data['address_id']
        payment_method = serializer.validated_data['payment_method']
        coupon_code = serializer.validated_data.get('coupon_code')

        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
            order = create_order_from_cart(cart, address_id, payment_method, coupon_code)
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=400)


class DeliveryAddressView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryAddressSerializer
    authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication)


    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication)


    def post(self, request, *args, **kwargs):
        order_id = request.data.get("order_id")
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            payment = Payment.objects.create(
                order=order,
                amount=order.total_price,
                currency='INR',
                payment_gateway='razorpay',
            )

            razorpay_order = create_razorpay_order(payment)

            payment.razorpay_order_id = razorpay_order['id']
            payment.save()


            return Response({
                'razorpay_order_id': razorpay_order['id'],
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
                'key_id': settings.RAZORPAY_KEY_ID,
                'order_id': order.id,
            })

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data
        order_id = data.get('order_id')
        payment_id = data.get('razorpay_payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')

        try:
            order = Order.objects.get(id=order_id, user=request.user)
            payment = Payment.objects.get(order_id=order_id)

            verify_razorpay_signature(payment_id, razorpay_order_id, signature)

            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = 'paid'
            payment.save()

            # Update order status
            order.status = 'completed'
            order.save()


            return Response({'message': 'Payment verified successfully'}, status=200)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)
        except Exception as e:
            order.payment_status = 'failed'
            order.save()
            return Response({'error': str(e)}, status=400)

# views/payment_webhook.py



@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        payload = request.body
        received_signature = request.headers.get("X-Razorpay-Signature")

        if not verify_webhook_signature(payload, received_signature):
            return Response({'detail': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        process_webhook_payload(payload)
        return Response({'detail': 'Webhook received'}, status=status.HTTP_200_OK)

class RetryPaymentView(APIView):
    def post(self, request, order_id):
        from payments.services.payment_service import retry_payment

        try:
            data = retry_payment(order_id)
            return Response(data, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

class RefundPaymentView(APIView):
    def post(self, request, payment_id):
        from payments.services.payment_service import refund_payment

        try:
            refund = refund_payment(payment_id)
            return Response({"refund_id": refund["id"]}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


# TnC
class TermsListView(generics.ListAPIView):
    queryset = TermsAndConditions.objects.filter(is_active=True)
    serializer_class = TermsAndConditionsSerializer
    permission_classes = [AllowAny]

class TermsCreateView(generics.CreateAPIView):
    queryset = TermsAndConditions.objects.all()
    serializer_class = TermsAndConditionsSerializer
    permission_classes = [IsAdminOrBDA]

# FAQ
class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]

class FAQCreateView(generics.CreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrBDA]

# Banner
class BannerListView(generics.ListAPIView):
    serializer_class = BannerSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        position = self.request.query_params.get('position')
        qs = Banner.objects.filter(is_active=True)
        if position:
            qs = qs.filter(position=position)
        return qs

class BannerCreateView(generics.CreateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    permission_classes = [IsAdminOrBDA]


class ShopAddressCreateView(generics.CreateAPIView):
    queryset = ShopAddress.objects.all()
    serializer_class = ShopAddressSerializer
    permission_classes = [permissions.IsAuthenticated]


class ShopAddressDetailView(generics.RetrieveUpdateAPIView):
    queryset = ShopAddress.objects.all()
    serializer_class = ShopAddressSerializer
    permission_classes = [permissions.IsAuthenticated]


class ShopDocumentCreateView(generics.CreateAPIView):
    queryset = ShopDocument.objects.all()
    serializer_class = ShopDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]


class ShopDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShopDocument.objects.all()
    serializer_class = ShopDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
