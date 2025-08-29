from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model


# Create your models here.
User = get_user_model()
class TermsAndConditions(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    version = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Terms v{self.version}"

class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question

class Banner(models.Model):
    POSITION_CHOICES = (
        ('top', 'Top of Homepage'),
        ('bottom', 'Bottom of Homepage'),
        ('middle', 'Middle of Homepage'),
        ('sidebar', 'Sidebar'),
    )

    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='banners/')
    redirect_url = models.URLField(blank=True, null=True)
    position = models.CharField(max_length=20, choices=POSITION_CHOICES)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)  # for sorting banners
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



    def __str__(self):
        return f"{self.title} - {self.position}"


class RecentlyVisitedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recent_visits')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-visited_at']
