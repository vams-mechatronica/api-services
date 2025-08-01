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

    path('products/',ProductListView.as_view()),

    path('subscriptions/', ProductSubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', ProductSubscriptionDetailView.as_view(), name='subscription-detail'),
    path('subscriptions/create/', CreateSimpleProductSubscriptionView.as_view(), name='simple-subscription-create'),

    path('customers/', CustomerProfileListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerProfileDetailView.as_view(), name='customer-detail'),

    path('vendors/', VendorProfileListCreateView.as_view(), name='vendor-list-create'),
    path('vendors/<int:pk>/', VendorProfileDetailView.as_view(), name='vendor-detail'),
    path('vendors/product/',VendorProductsListView.as_view(),name="vendor-product-list"),

    path('bdas/', BDAProfileListCreateView.as_view(), name='bda-list-create'),
    path('bdas/<int:pk>/', BDAProfileDetailView.as_view(), name='bda-detail'),

    path('bank-details/', BankDetailListCreateView.as_view(), name='bank-list-create'),
    path('bank-details/<int:pk>/', BankDetailDetailView.as_view(), name='bank-detail'),

    path('wallet/balance/', WalletBalanceView.as_view()),
    path('wallet/recharge/', RechargeWalletAPI.as_view()),
    path('wallet/recharge/initiate/', InitiateWalletRechargeAPI.as_view(), name='wallet-recharge-initiate'),
    path('wallet/recharge/verify/', VerifyWalletRechargeAPI.as_view(), name='wallet-recharge-verify'),
    path('wallet/deduct-vendor-access/', VendorDailyAccessAPI.as_view()),

    path('cart/', CartView.as_view(), name='cart-detail'),
    path('cart/add/', AddCartItemView.as_view(), name='cart-add-item'),

    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', CreateOrderView.as_view(), name='create-order'),

    path('payment/initiate/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='verify-payment'),

    path("webhook/razorpay/", RazorpayWebhookView.as_view(), name="razorpay-webhook"),
    path("refund/<int:payment_id>/", RefundPaymentView.as_view(), name="refund-payment"),
    path("retry/<int:order_id>/", RetryPaymentView.as_view(), name="retry-payment"),

    path('address/', DeliveryAddressView.as_view(), name='address-list-create'),

    path('tnc/', TermsListView.as_view(), name='tnc-list'),
    path('tnc/create/', TermsCreateView.as_view(), name='tnc-create'),

    # FAQ
    path('faq/', FAQListView.as_view(), name='faq-list'),
    path('faq/create/', FAQCreateView.as_view(), name='faq-create'),

    # Banner
    path('banners/', BannerListView.as_view(), name='banner-list'),
    path('banners/create/', BannerCreateView.as_view(), name='banner-create'),
]
