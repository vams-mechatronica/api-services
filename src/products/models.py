
from django.db import models
from category.models import Category
from accounts.models import VendorProfile
from utils.g_uuid import GenerateUUID
from django_quill.fields import QuillField
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _



class Product(models.Model):
    PRODUCT_TYPES = (
        ('food', 'Food'),
        ('electronic', 'Electronic'),
        ('service', 'Service'),
        # Add more as needed
    )

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=120, null=True, blank=True)
    sku = models.CharField(max_length=100, unique=True, default=GenerateUUID.generate_sku(prefix='VAMS-SKU'))
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    unit = models.ForeignKey("Unit", verbose_name=_("unit"), on_delete=models.SET_NULL,null=True, blank=True)
    image = models.ImageField(upload_to='products/', null=True,blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Unit(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20)
    product_type = models.CharField(max_length=20, choices=Product.PRODUCT_TYPES)

    def __str__(self):
        return f"{self.name} ({self.code})"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    image = models.ImageField(upload_to='item_images/', max_length=500)

    def __str__(self):
        return f"{self.product.name} Image"

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

class FoodDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='food_detail')
    ingredients = models.TextField(blank=True)
    is_vegetarian = models.BooleanField(default=True)
    calories = models.PositiveIntegerField(null=True, blank=True)

class ElectronicDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='electronic_detail')
    brand = models.CharField(max_length=255)
    warranty_months = models.PositiveIntegerField(default=0)
    power_usage = models.CharField(max_length=50, blank=True, null=True)

class ServiceDetail(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='service_detail')
    service_duration_minutes = models.PositiveIntegerField()
    warranty_days = models.PositiveIntegerField(blank=True, null=True)
    service_type = models.CharField(max_length=255)

