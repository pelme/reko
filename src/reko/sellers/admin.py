from django.contrib import admin

from .models import Category, Seller


class SellerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category)
admin.site.register(Seller, SellerAdmin)
