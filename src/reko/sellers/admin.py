from django.contrib import admin

from .models import Category, Seller, SellerImage


class SellerImageInline(admin.TabularInline):
    model = SellerImage


class SellerAdmin(admin.ModelAdmin):
    inlines = [SellerImageInline]


admin.site.register(Category)
admin.site.register(Seller, SellerAdmin)
