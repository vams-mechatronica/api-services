from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.services import OTPService
from .authenticator import AuthenticationService, UserService
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.authentication import TokenAuthentication, BasicAuthentication, SessionAuthentication
from .permissions import *
from .serializers import *
user = get_user_model()

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

        if not phone_number or not otp:
            return Response({'error': 'Phone number and OTP required.'}, status=status.HTTP_400_BAD_REQUEST)

        auth_service = AuthenticationService()
        if auth_service.verify_login_otp(phone_number, otp):
            user_service = UserService(use_jwt=True)  # or False for Django Token
            cuser, created = user_service.get_or_create_user(phone_number.replace('+',''))
            token = user_service.generate_token(cuser)
            if not cuser:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': 'Login successful.', 'user_id': cuser.id, 'token':token}, status=status.HTTP_200_OK)
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
        return FoodProduct.objects.filter(vendor=vendor)

    def perform_create(self, serializer):
        vendor = VendorProfile.objects.get(user=self.request.user)
        if vendor.category.name.lower() != "restaurant":
            raise PermissionDenied("Only Restaurant vendors can add food products.")
        serializer.save(vendor=vendor)

# GET, PUT, PATCH, DELETE
class FoodProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = FoodProduct.objects.all()
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
    serializer_class = VendorProfileSerializer


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
            return FoodProduct.objects.none()
        return FoodProduct.objects.filter(vendor_id=vendor_id)

    def list(self, request, *args, **kwargs):
        vendor_id = self.request.GET.get('vendor_id')
        if not vendor_id:
            return Response({'message': 'vendor_id is compulsory'}, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
    
    