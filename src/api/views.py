from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.services import OTPService
from .authenticator import AuthenticationService
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
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
            cuser, created = user.objects.get_or_create(phone_number=phone_number)
            if role and created:
                cuser.phone_number = phone_number
                cuser.role = role.lower()
                cuser.set_unusable_password()
                cuser.save()

            return Response({'message': 'Signup successful.', 'user_id': cuser.id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)



class RequestLoginOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({'error': 'Phone number required.'}, status=status.HTTP_400_BAD_REQUEST)

        auth_service = AuthenticationService()
        auth_service.send_login_otp(phone_number)

        return Response({'message': 'OTP sent via WhatsApp.'})


class VerifyLoginOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp = request.data.get('otp')

        if not phone_number or not otp:
            return Response({'error': 'Phone number and OTP required.'}, status=status.HTTP_400_BAD_REQUEST)

        auth_service = AuthenticationService()
        if auth_service.verify_login_otp(phone_number, otp):
            cuser = user.objects.filter(phone_number=phone_number).first()
            if not cuser:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            return Response({'message': 'Login successful.', 'user_id': cuser.id}, status=status.HTTP_200_OK)
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


