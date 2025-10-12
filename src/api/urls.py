from django.urls import path,include
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('signup/generate-otp',RequestSignupOTP.as_view()),
    path('signup/verify-otp',VerifySignupOTP.as_view()),
    path('login/request-otp', RequestLoginOTP.as_view()),
    path('login/verify-otp', VerifyLoginOTP.as_view()),
    path('login/password', PasswordLogin.as_view()),
    
    # user
    path("user/", UserDetailAPIView.as_view(), name="user-details"),
    path('user/sync-address/', SyncAddressView.as_view(), name='sync-address'),
    path("user/addresses/", UserAddressListCreateAPIView.as_view(), name="user-addresses"),

    # category
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    # products 
    path('food-products/', FoodProductListCreateView.as_view()),
    path('food-products/<int:pk>/', FoodProductDetailView.as_view()),

    path('products/',ProductListView.as_view()),
    path('product/<int:pk>/',ProductRetrieveAPI.as_view()),
    path('product/<slug:slug>/', ProductRetrieveBySlugAPI.as_view()),
    path("products/<int:pk>/related/", RelatedProductsView.as_view(), name="related-products"),
    path("products/<slug:slug>/related/", RelatedProductsSlugView.as_view(), name="related-products-slug"),
    
    path('units/', UnitListView.as_view(), name='unit-list'),
    path('subscriptions/', ProductSubscriptionListCreateView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', ProductSubscriptionDetailView.as_view(), name='subscription-detail'),
    path('subscriptions/create/', CreateSimpleProductSubscriptionView.as_view(), name='simple-subscription-create'),

    path('customers/', CustomerProfileListCreateView.as_view(), name='customer-list-create'),
    path('customers/<int:pk>/', CustomerProfileDetailView.as_view(), name='customer-detail'),
    path('vendors/', VendorProfileListCreateView.as_view(), name='vendor-list-create'),
    path('vendors/dashboard/', VendorDashboardAPI.as_view(), name='vendor-dashboard'),
    path('vendors/stores/', VendorStoreView.as_view(), name='vendor-store-list'),
    path('vendors/stores/<slug:slug>/', VendorStoreDetailView.as_view(), name='vendor-store-detail'),
    path('vendors/stores/<slug:slug>/products/', VendorStoreProductsListView.as_view(), name='vendor-store-products'),
    path('vendors/<int:pk>/', VendorProfileDetailView.as_view(), name='vendor-detail'),
    path('vendors/<int:pk>/image-update/', VendorProfileImageUploadView.as_view(), name='vendor-detail'),
    path('vendors/products/',VendorProductsListView.as_view(),name="vendor-product-list"),
    path('vendors/product/<int:pk>',VendorProductsUpdateView.as_view(),name="vendor-product-update"),

    path('vendors/shop-address/', ShopAddressCreateView.as_view(), name='create-shop-address'),
    path('vendors/shop-address/<int:pk>/', ShopAddressDetailView.as_view(), name='shop-address-detail'),
    path('vendors/orders/',VendorOrderAPI.as_view()),
    path('vendors/orders/items/',VendorOrderItemsAPI.as_view()),
    path('vendors/shop-documents/', ShopDocumentCreateView.as_view(), name='create-shop-document'),
    path('vendors/shop-documents/<int:pk>/', ShopDocumentDetailView.as_view(), name='shop-document-detail'),
    path('vendors/shop-documents/files/', ShopDocumentFileListCreateView.as_view(), name='shop-documents-files-list-create'),
    path('vendors/shop-documents/files/<int:pk>/', ShopDocumentFileDetailView.as_view(), name='shop-documents-files-detail'),
    path('bdas/', BDAProfileListCreateView.as_view(), name='bda-list-create'),
    path('bdas/<int:pk>/', BDAProfileDetailView.as_view(), name='bda-detail'),

    path('bank-details/', BankDetailListCreateView.as_view(), name='bank-list-create'),
    path('vendors/bank-details/', VendorBankDetailsListCreateView.as_view(), name='vendor-bank-list-view'),
    path('bank-details/<int:pk>/', BankDetailDetailView.as_view(), name='bank-detail'),

    path('coupons/', CouponListCreateView.as_view(), name='coupon-list-create'),
    path('coupons/<int:pk>/', CouponRetrieveUpdateDeleteView.as_view(), name='coupon-detail'),
    path('apply-coupon/', ApplyCouponView.as_view(), name='apply-coupon'),
    path('vendors/coupons/', VendorCouponListCreateView.as_view(), name='vendor-coupon-list-create'),
    path('vendors/coupons/<int:pk>/', VendorCouponRetrieveUpdateDeleteView.as_view(), name='vendor-coupon-detail'),

    path('wallet/balance/', WalletBalanceView.as_view()),
    path('wallet/recharge/', RechargeWalletAPI.as_view()),
    path('wallet/transactions/', WalletTransactionAPI.as_view()),
    path('wallet/recharge/initiate/', InitiateWalletRechargeAPI.as_view(), name='wallet-recharge-initiate'),
    path('wallet/recharge/verify/', VerifyWalletRechargeAPI.as_view(), name='wallet-recharge-verify'),
    path('wallet/deduct-vendor-access/', VendorDailyAccessAPI.as_view()),

    path('cart/', CartView.as_view(), name='cart-detail'),
    path('cart/add/', AddCartItemView.as_view(), name='cart-add-item'),
    path('cart/update/', UpdateCartItemView.as_view(), name='cart-update'),
    path('cart/delete/<int:product_id>/', DeleteCartItemView.as_view(), name='cart-delete'),

    path('orders/', OrderListView.as_view(), name='order-list'),
    path('order/<int:pk>/',OrderRetrieveAPI.as_view(), name='order-retrieve'),
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

    # JWT
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),

    path('check-delivery', CheckDeliveryAvailabilityAPI.as_view(), name='check-delivery'),
    path('header-counts/', HeaderCountsAPI.as_view(), name='header-counts'),

    path("webhook/whatsapp/status/", WhatsAppDeliveryStatusWebhook.as_view(), name="whatsapp-status-webhook"),
    path("webhook/whatsapp/inbound/", InboundWhatsAppMessageWebhook.as_view(), name="whatsapp-inbound-webhook"),
    path("marketing/contacts/import/", ImportContactsAPIView.as_view(), name="import-contacts"),
]
