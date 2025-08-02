from django.contrib import admin
from .models import Category, CategoryRefundRule, CategorySubscriptionPlan

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name','is_active','created_at')

@admin.register(CategoryRefundRule)
class CategoryRefundRuleAdmin(admin.ModelAdmin):
    list_display = ('category','return_allowed')

@admin.register(CategorySubscriptionPlan)
class CategorySubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('category','cost','frequency')
    

    

    
