from django.contrib.auth import get_user_model
from category.models import *
from products.models import *
from payments.models import *
from accounts.models import *
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
    class Meta:
        model = Category
        fields = '__all__'

class FoodProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodProduct
        fields = '__all__'
        read_only_fields = ['vendor']

class ElectronicProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElectronicProduct
        fields = '__all__'
        read_only_fields = ['vendor']

class ServiceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProduct
        fields = '__all__'
        read_only_fields = ['vendor']

class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = '__all__'

class VendorProfileSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    class Meta:
        model = VendorProfile
        fields = '__all__'
    
    def get_category_name(self,obj):
        return obj.category.name

class BDAProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BDAProfile
        fields = '__all__'

class BankDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankDetail
        fields = '__all__'

    