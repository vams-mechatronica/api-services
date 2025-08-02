from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.urls import reverse



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    image = models.ImageField(upload_to="category/", null=True,blank=True)
    parent_category = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='subcategories')
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, max_length=120, verbose_name=_("Slug"),null=True,blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated At"), auto_now=True)
    
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Category")

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class CategoryRefundRule(models.Model):
    category = models.OneToOneField(Category, on_delete=models.CASCADE, related_name="refund_rules")
    return_allowed = models.BooleanField(default=False)
    return_window_days = models.PositiveIntegerField(default=0)
    refund_type_choices = [
        ('wallet', 'Wallet'),
        ('original', 'Original Payment Method'),
        ('none', 'No Refund')
    ]
    refund_type = models.CharField(max_length=10, choices=refund_type_choices, default='none')

    class Meta:
        verbose_name = _("CategoryRefundRule")
        verbose_name_plural = _("CategoryRefundRules")

    def __str__(self):
        return self.category.name

    def get_absolute_url(self):
        return reverse("CategoryRefundRule_detail", kwargs={"pk": self.pk})


class CategorySubscriptionPlan(models.Model):
    FREQUENCY_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )

    category = models.OneToOneField(Category, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)

    class Meta:
        verbose_name = _("CategorySubscriptionPlan")
        verbose_name_plural = _("CategorySubscriptionPlans")

    def __str__(self):
        return f"{self.category.name} - ₹{self.cost} ({self.frequency})"
    
    def get_absolute_url(self):
        return reverse("CategorySubscriptionPlan_detail", kwargs={"pk": self.pk})
    

