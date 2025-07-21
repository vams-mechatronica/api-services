
from django.db import models
from category.models import Category
from accounts.models import VendorProfile
from utils.g_uuid import GenerateUUID
from django_quill.fields import QuillField
from django.contrib.contenttypes.fields import GenericForeignKey,GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class ProductImage(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    product = GenericForeignKey('content_type', 'object_id')
    alt_text = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    image = models.ImageField(upload_to='item_images/', max_length=500)

    def __str__(self):
        return f"{self.product.name} Image"

    class Meta:
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

class BaseProduct(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=120, verbose_name=_("Slug"),null=True,blank=True)
    sku = models.CharField(max_length=100, unique=True, default=GenerateUUID.generate_sku(prefix='VAMS-SKU'))
    vendor = models.ForeignKey(VendorProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/')
    images = GenericRelation(ProductImage, related_query_name='images')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            # Automatically generate slug from name if not provided
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True

class FoodProduct(BaseProduct):
    ingredients = models.TextField(blank=True)
    is_vegetarian = models.BooleanField(default=True)
    calories = models.PositiveIntegerField(null=True, blank=True)

class ElectronicProduct(BaseProduct):
    brand = models.CharField(max_length=255)
    warranty_months = models.PositiveIntegerField(default=0)
    power_usage = models.CharField(max_length=50, blank=True, null=True)

class ServiceProduct(BaseProduct):
    service_duration_minutes = models.PositiveIntegerField()
    warranty_days = models.PositiveIntegerField(blank=True, null=True)
    service_type = models.CharField(max_length=255)

