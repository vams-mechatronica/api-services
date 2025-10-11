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
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils import CustomPagePagination
from .permissions import *
from .serializers import *
from datetime import date
user = get_user_model()
import hmac, hashlib, json
import pandas as pd
from django.db import IntegrityError,InterfaceError, InternalError
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from cart.services.cart_service import add_or_update_cart_item
from orders.services.order_service import create_order_from_cart
from payments.services.payment_service import RazorpayService
from scheduler.services.subscription_service import check_wallet_balance_and_update
from notifications.services import enqueue_message

class RequestSignupOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)

        otp_service = OTPService()
        otp_service.generate_otp(phone_number, send_as_sms=False)

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

            if created:
                # Wallet
                userWallet, wcreated = Wallet.objects.get_or_create(user=cuser)
                if wcreated:
                    userWallet.balance = 0
                    userWallet.save()
            if not cuser:
                return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
            if role and role == 'bda':
                bdaObj = get_object_or_404(BDAProfile,user=cuser)
                if bdaObj:
                    bdaUserId = bdaObj.pk
            return Response({'message': 'Login successful.', 'user_id': cuser.id,'bdaUserId':bdaUserId, 'token':token}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

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
    authentication_classes = []
    queryset = Category.objects.annotate(count=Count('product')).order_by('-updated_at')
    serializer_class = CategorySerializer
    pagination_class = CustomPagePagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['parent_category','parent_category__slug', 'is_active'] 

    def get_permissions(self):
        if self.request.method in ['POST']:
            return [permissions.IsAuthenticated(), IsAdminOrBDA()]
        return [permissions.AllowAny()]
    
    def get_queryset(self):
        if_parent_category = self.request.GET.get('parent_category_only',False)
        if if_parent_category:
            return self.queryset.filter(parent_category=None)

        return self.queryset.exclude(parent_category=None)

# GET: Retrieve, PUT/PATCH: Update, DELETE (Admin/BDA only)
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminBDAorVendor,)
    #authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication,JWTAuthentication)

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsAdminOrBDA()]
        return [permissions.AllowAny()]


# Products 

###### Food Products

# GET (List) + POST (Create)
class FoodProductListCreateView(generics.ListCreateAPIView):
    serializer_class = FoodProductSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminBDAorVendor]
    #authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication,JWTAuthentication)


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
    permission_classes = [permissions.IsAuthenticated, IsAdminBDAorVendor]
    #authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication,JWTAuthentication)

# --- Customer Profile CRUD ---
class CustomerProfileListCreateView(generics.ListCreateAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer


class CustomerProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CustomerProfile.objects.all()
    permission_classes = (IsAdminBDAorVendor,)
    #authentication_classes = (TokenAuthentication,JWTAuthentication,BasicAuthentication,SessionAuthentication)
    serializer_class = CustomerProfileSerializer


class UserDetailAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializerDetail
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return User.objects.get(id=self.request.user.id)

# --- API to get user addresses ---

class UserAddressListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class SyncAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        # Check if an identical address already exists for this user
        existing = DeliveryAddress.objects.filter(
            user=user,
            name=data.get('name'),
            address_line=data.get('address_line'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            phone_number=data.get('phone_number')
        ).first()

        if existing:
            # address already present, nothing to do
            serializer = DeliveryAddressSerializer(existing)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If address exists but some fields changed (same user, same line1 but diff city etc.)
        # You can choose your match criteria
        partial_match = DeliveryAddress.objects.filter(user=user, line1=data.get('line1')).first()
        if partial_match:
            serializer = DeliveryAddressSerializer(partial_match, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Otherwise create new
        serializer = DeliveryAddressSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# --- Vendor Profile CRUD ---
class VendorStoreView(generics.ListAPIView):
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ('shop_name',)
    filterset_fields = ('sub_category','category')
    permission_classes = (AllowAny,)
    authentication_classes = ()
    queryset = VendorProfile.objects.all().order_by('-updated_at') 
    serializer_class = VendorProfileSerializer

class VendorStoreDetailView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    queryset = VendorProfile.objects.all()
    serializer_class = VendorDetailSerializer
    lookup_field = 'slug'

class VendorStoreProductsListView(generics.ListAPIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    serializer_class = ProductSimpleSerializer

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        return Product.objects.filter(vendor__slug=slug)


class VendorProfileListCreateView(generics.ListCreateAPIView):
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ('shop_name',)
    filterset_fields = ('sub_category','category')
    permission_classes = (IsAdminBDAorVendor,)
    #authentication_classes = (JWTAuthentication,SessionAuthentication)
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

class VendorBankDetailsListCreateView(generics.ListCreateAPIView):
    serializer_class = BankDetailSerializer
    permission_classes = (IsAdminBDAorVendor,)
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def get_queryset(self):
        vendor_id = self.request.GET.get('vendor_id')
        if not vendor_id:
            return BankDetail.objects.none()

        vendor_ct = ContentType.objects.get_for_model(VendorProfile)
        return BankDetail.objects.filter(content_type=vendor_ct, object_id=vendor_id)

    def list(self, request, *args, **kwargs):
        vendor_id = self.request.GET.get('vendor_id')
        if not vendor_id:
            return Response({'message': 'vendor_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        vendor_id = request.data.get('vendor_id')
        if not vendor_id:
            return Response({'message': 'vendor_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = VendorProfile.objects.get(id=vendor_id)
        except VendorProfile.DoesNotExist:
            return Response({'message': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)

        vendor_ct = ContentType.objects.get_for_model(VendorProfile)
        data = request.data.copy()
        data['content_type'] = vendor_ct.id
        data['object_id'] = vendor.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class VendorProductsListView(generics.ListCreateAPIView):
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    permission_classes = (IsAdminBDAorVendor,)
    serializer_class = ProductSerializer

    def get_queryset(self):
        vendor_id = self.request.GET.get('vendor_id')
        if not vendor_id:
            return Product.objects.none()
        return Product.objects.filter(vendor_id=vendor_id)

    def list(self, request, *args, **kwargs):
        vendor_id = self.request.GET.get('vendor_id')
        if not vendor_id:
            return Response({'message': 'vendor_id is compulsory'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

class VendorProductsUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated,)
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class WalletBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        return Response(WalletSerializer(wallet).data)

class RechargeWalletAPI(APIView):
    permission_classes = (IsAuthenticated,)
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    
    def post(self,request,*args, **kwargs):
        amount = request.data.get('amount')
        if not amount:
            return Response({"error": "Amount required"}, status=400)
        
        wallet = Wallet.objects.get(user=request.user)
        wallet.add_funds(amount)
        WalletTransaction.objects.create(wallet=wallet, amount=amount, transaction_type='credit', description="Wallet recharge")
        
        return Response({"message": "Recharge successful", "balance": wallet.balance})

class WalletTransactionAPI(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WalletTransactionSerializer

    def get_queryset(self):
        wallet = Wallet.objects.get(user = self.request.user)
        queryset = WalletTransaction.objects.filter(wallet=wallet).order_by('-timestamp')
        return queryset
    

# views.py
class InitiateWalletRechargeAPI(APIView):
    permission_classes = [IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def post(self, request):
        amount = float(request.data.get('amount'))
        if not amount or amount <= 0:
            return Response({"error": "Valid amount required"}, status=400)

        wallet = Wallet.objects.get(user=request.user)
        receipt_id = f"wallet_recharge_{request.user.id}_{timezone.now().timestamp()}"
        order = RazorpayService().create_wallet_recharge_order(amount=amount, receipt_id=receipt_id)

        WalletRecharge.objects.create(
            wallet=wallet,
            amount=amount,
            razorpay_order_id=order['id']
        )

        return Response({
            "order_id": order['id'],
            "currency": order['currency'],
            "amount": order['amount'],
            "razorpay_key": settings.RAZORPAY_KEY_ID
        })

class VerifyWalletRechargeAPI(APIView):
    permission_classes = [AllowAny]  # Or secure it via Razorpay webhook signature

    def post(self, request):
        data = request.data
        try:
            RazorpayService().verify_payment_signature(
                data['data'].get('razorpay_order_id'),
                data['data'].get('razorpay_payment_id'),
                data['data'].get('razorpay_signature')
            )

            recharge = WalletRecharge.objects.get(razorpay_order_id=data['data']['razorpay_order_id'])
            if recharge.status != 'success':
                recharge.mark_successful(data['data']['razorpay_payment_id'],data['data']['razorpay_signature'])

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
    aauthentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
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
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    permission_classes = (AllowAny,)
    serializer_class = ProductSimpleSerializer
    queryset = Product.objects.all().select_related('category', 'vendor').prefetch_related('images')

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['category','category__slug','vendor__id','vendor','category__is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'updated_at', 'stock']
    ordering = ['-created_at']  # default order

class ProductRetrieveAPI(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSimpleSerializer
    queryset = Product.objects.all().select_related('category', 'vendor').prefetch_related('images')

class ProductRetrieveBySlugAPI(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductSimpleSerializer
    queryset = Product.objects.select_related('category', 'vendor').prefetch_related('images')
    lookup_field = 'slug'  # this is the key change


class RelatedProductsView(generics.ListAPIView):
    serializer_class = ProductSimpleSerializer

    def get_queryset(self):
        pk = self.kwargs.get("pk")
        product = Product.objects.filter(pk=pk).first()
        if not product:
            return Product.objects.none()

        return (
            Product.objects.filter(category=product.category)
            .exclude(id=product.id)[:4]
        )

class RelatedProductsSlugView(generics.ListAPIView):
    serializer_class = ProductSimpleSerializer

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        product = Product.objects.filter(slug=slug).first()
        if not product:
            return Product.objects.none()

        return (
            Product.objects.filter(category=product.category)
            .exclude(id=product.id)[:4]
        )


class ProductSubscriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['frequency', 'status', 'product']

    def get_queryset(self):
        subscriptions = ProductSubscription.objects.filter(user=self.request.user).order_by('-created_at')
        for sub in subscriptions:
            check_wallet_balance_and_update(sub)
        return subscriptions

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Retrieve, Update, Delete
class ProductSubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def get_queryset(self):
        return ProductSubscription.objects.filter(user=self.request.user.id)

class CreateSimpleProductSubscriptionView(generics.GenericAPIView):
    serializer_class = SimpleProductSubscriptionCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            subscription = serializer.save()
        except IntegrityError:
            return Response({
                'message':'Subscription already exists'
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": "Subscription created successfully.",
            "subscription_id": subscription.id
        }, status=status.HTTP_201_CREATED)

class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

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
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    serializer_class = CartSerializer

    def get_object(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return cart


class AddCartItemView(APIView):
    """This api will be used to add or remove cart items. To remove cart items just pass quantity as 0"""
    permission_classes = [IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = add_or_update_cart_item(cart, product_id, quantity)

        return Response({'message': 'Item updated successfully','id':cart.id}, status=200)

class UpdateCartItemView(APIView):
    """Update quantity of a cart item"""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item = add_or_update_cart_item(cart, product_id, quantity)

        return Response(
            {"message": "Cart item updated successfully"},
            status=status.HTTP_200_OK
        )


class DeleteCartItemView(APIView):
    """Delete a cart item by product_id"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(cart.items, product__id=product_id)
        item.delete()

        return Response(
            {"message": "Cart item deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )



class OrderListView(generics.ListAPIView):
    """
    List all orders placed by the authenticated user.

    Returns a list of orders associated with the currently authenticated user,
    including order details such as items, totals, payment status, and delivery information.

    Permissions:
        - User must be authenticated
    """
    permission_classes = [IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderRetrieveAPI(generics.RetrieveAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer



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
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)


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
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)


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

            razorpay_order = RazorpayService().create_order_for_purchase(payment)

            payment.razorpay_order_id = razorpay_order['id']
            payment.save()


            return Response({
                'order_id': order.id,
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key': settings.RAZORPAY_KEY_ID,
                'amount': razorpay_order['amount'],
                'currency': razorpay_order['currency'],
            })

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)

class VerifyPaymentView(APIView):
    permission_classes = [AllowAny]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

    def post(self, request, *args, **kwargs):
        data = request.data
        payment_id = data['data'].get('razorpay_payment_id')
        razorpay_order_id = data['data'].get('razorpay_order_id')
        signature = data['data'].get('razorpay_signature')

        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            order = Order.objects.get(id=payment.order.id, user=request.user)

            paymentVerificationStatus = RazorpayService().verify_payment_signature(razorpay_order_id, payment_id, signature)

            payment.razorpay_payment_id = payment_id
            payment.razorpay_signature = signature
            payment.status = 'paid'
            payment.save()

            # Update order status
            order.status = 'completed'
            order.save()

            # clear cart after payment success.
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()

            enqueue_message(recipient='info@vamsmechatronica.in',
                subject="Order Created",
                body=f"order #{order.id} has been created successfully.",
                channel='email')


            return Response({'message': 'Payment verified successfully'}, status=200)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=404)
        except Exception as e:
            payment.status = 'failed'
            order.status = 'payment-failed'
            order.save()
            return Response({'error': str(e)}, status=400)

# views/payment_webhook.py



@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        payload = request.body
        received_signature = request.headers.get("X-Razorpay-Signature")

        if not RazorpayService().verify_webhook_signature(payload, received_signature):
            return Response({'detail': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)

        RazorpayService().process_webhook_payload(payload)
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
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

# FAQ
class FAQListView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_active=True)
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    

class FAQCreateView(generics.CreateAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsAdminOrBDA]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

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
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)


class ShopAddressCreateView(generics.ListCreateAPIView):
    queryset = ShopAddress.objects.all()
    serializer_class = ShopAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = (BasicAuthentication,TokenAuthentication,SessionAuthentication,JWTAuthentication)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vendor']

class ShopAddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShopAddress.objects.all()
    serializer_class = ShopAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)


class ShopDocumentCreateView(generics.ListCreateAPIView):
    queryset = ShopDocument.objects.all()
    serializer_class = ShopDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['vendor']
    

class ShopDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShopDocument.objects.all()
    serializer_class = ShopDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

class ShopDocumentFileListCreateView(generics.ListCreateAPIView):
    queryset = ShopDocumentFile.objects.all()
    serializer_class = ShopDocumentFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = [BasicAuthentication, SessionAuthentication, TokenAuthentication, JWTAuthentication]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['shop_doc']  # So you can filter files by ShopDocument

class ShopDocumentFileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ShopDocumentFile.objects.all()
    serializer_class = ShopDocumentFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    #authentication_classes = [BasicAuthentication, SessionAuthentication, TokenAuthentication, JWTAuthentication]


class CouponListCreateView(generics.ListCreateAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = (IsAuthenticated,)
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

class CouponRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = (IsAuthenticated,)
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)

class ApplyCouponView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        code = request.data.get("code")
        try:
            coupon = Coupon.objects.get(code=code)
            cart = Cart.objects.get(user=request.user)

            if not coupon.active:
                return Response({"error": "Coupon expired or inactive"}, status=400)

            if cart.get_total() < coupon.min_order_amount:
                return Response({"error": "Minimum order amount not met"}, status=400)

            cart.coupon = coupon
            cart.save()

            return Response({
                "success": True,
                "discounted_total": cart.get_total(),
                "coupon": coupon.code
            })
        except Coupon.DoesNotExist:
            return Response({"error": "Invalid coupon code"}, status=400)

class VendorCouponListCreateView(generics.ListCreateAPIView):
    serializer_class = VendorCouponSerializer
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        vendor_id = self.request.GET.get('vendor_id')
        if vendor_id:
            return VendorCoupon.objects.filter(vendor_id=vendor_id)
        return VendorCoupon.objects.none()

    def list(self, request, *args, **kwargs):
        vendor_id = request.GET.get('vendor_id')
        if not vendor_id:
            return Response({"message": "vendor_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class VendorCouponRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VendorCoupon.objects.all()
    serializer_class = VendorCouponSerializer
    lookup_field = 'pk'
    permission_classes = (IsAuthenticated,)
    #authentication_classes = (BasicAuthentication, TokenAuthentication, SessionAuthentication,JWTAuthentication)


class UnitListView(generics.ListAPIView):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product_type'] 

class CheckDeliveryAvailabilityAPI(APIView):
    def get(self, request, *args, **kwargs):
        """
        GET /api/v1/check-delivery/?pincode=110001&sector=Sector-5
        """
        pincode = request.query_params.get('pincode')
        sector = request.query_params.get('sector')

        if not pincode:
            return Response({"error": "pincode is required"}, status=400)

        queryset = DeliveryArea.objects.filter(
            pincode=pincode, is_active=True
        )
        if sector:
            queryset = queryset.filter(sector=sector)
        
        exists = queryset.exists()

        return Response({
            "pincode": pincode,
            "sector": sector,
            "deliverable": exists,
            "message":"We are delivering at this location." if exists else "Sorry! Currently, We are not delivering at this location."
        })


class HeaderCountsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_count = (
            CartItem.objects
            .filter(cart__user=request.user)
            .aggregate(total_qty=Sum('quantity'))
        )['total_qty'] or 0 
        subscription_count = ProductSubscription.objects.filter(user=request.user, status='active').count()
        return Response({
            'cart_count': cart_count,
            'subscription_count': subscription_count
        })

@method_decorator(csrf_exempt, name="dispatch")
class WhatsAppDeliveryStatusWebhook(APIView):
    """
    Webhook for Twilio to send delivery status updates
    """

    def post(self, request, *args, **kwargs):
        data = request.data

        message_sid = data.get("MessageSid")
        if not message_sid:
            return Response({"error": "MessageSid missing"}, status=status.HTTP_400_BAD_REQUEST)

        msg, created = WhatsAppMessage.objects.get_or_create(SID=message_sid)

        msg.account_sid = data.get("AccountSid")
        msg.messaging_service_sid = data.get("MessagingServiceSid")
        msg.to = data["To"].replace('whatsapp:','')
        msg.from_number = data["From"].replace('whatsapp:','')
        msg.body = data.get("Body")
        msg.status = data.get("MessageStatus")
        msg.error_code = data.get("ErrorCode")
        msg.error_message = data.get("ErrorMessage")
        msg.num_segments = int(data.get("NumSegments", 1))
        msg.api_version = data.get("ApiVersion")
        msg.price = data.get("Price")
        msg.price_unit = data.get("PriceUnit")
        msg.direction = data.get("Direction")

        msg.save()

        return Response({"message": "Status updated"}, status=status.HTTP_200_OK)



@method_decorator(csrf_exempt, name="dispatch")
class InboundWhatsAppMessageWebhook(APIView):
    """
    Webhook for inbound messages from users
    """

    def post(self, request, *args, **kwargs):
        message_sid = request.data.get("MessageSid")
        from_number = request.data.get("From")
        to_number = request.data.get("To")
        body = request.data.get("Body")

        inbound, created = InboundWhatsAppMessage.objects.get_or_create(
            SID=message_sid,
            defaults={
                "from_number": from_number,
                "to": to_number,
                "body": body,
            }
        )

        serializer = InboundWhatsAppMessageSerializer(inbound)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ImportContactsAPIView(APIView):
    """
    Upload Excel file and import contacts into MarketingContact
    """

    def post(self, request, *args, **kwargs):
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file)

            imported, skipped = 0, 0
            for _, row in df.iterrows():
                phone = str(row.get("phone_number")).strip()
                name = row.get("name", "")

                if phone:

                    # Ensure phone number has +91 prefix
                    if not phone.startswith("+91"):
                        # remove leading 0 if present
                        if phone.startswith("0"):
                            phone = phone[1:]
                        elif phone.startswith("91"):
                            phone = phone.removeprefix("91")
                        phone = f"+91{phone}"

                    _, created = MarketingContact.objects.get_or_create(
                        phone_number=phone,
                        defaults={"name": name}
                    )
                    if created:
                        imported += 1
                    else:
                        skipped += 1

            return Response(
                {
                    "message": "Contacts import completed",
                    "imported": imported,
                    "skipped_existing": skipped,
                    "total_in_file": len(df),
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
