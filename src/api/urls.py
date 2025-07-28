from django.urls import path,include
from .views import *

urlpatterns = [
    path('signup/generate-otp',RequestSignupOTP.as_view()),
    path('signup/verify-otp',VerifySignupOTP.as_view()),
    path('login/request-otp', RequestLoginOTP.as_view()),
    path('login/verify-otp', VerifyLoginOTP.as_view()),
    path('login/password', PasswordLogin.as_view()),

    # category
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # products 
    path('food-products/', FoodProductListCreateView.as_view()),
    path('food-products/<int:pk>/', FoodProductDetailView.as_view()),

    path('customers/', CustomerProfileListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerProfileDetailView.as_view(), name='customer-detail'),

    path('vendors/', VendorProfileListCreateView.as_view(), name='vendor-list-create'),
    path('vendors/<int:pk>/', VendorProfileDetailView.as_view(), name='vendor-detail'),
    path('vendors/product/',VendorProductsListView.as_view(),name="vendor-product-list"),

    path('bdas/', BDAProfileListCreateView.as_view(), name='bda-list-create'),
    path('bdas/<int:pk>/', BDAProfileDetailView.as_view(), name='bda-detail'),

    path('bank-details/', BankDetailListCreateView.as_view(), name='bank-list-create'),
    path('bank-details/<int:pk>/', BankDetailDetailView.as_view(), name='bank-detail'),
]
