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
]
