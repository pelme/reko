from django.contrib import admin

from .models import Order, OrderProduct


class OrderProductInline(admin.TabularInline):
    model = OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["full_order_number", "full_name", "total_price"]
    list_filter = ["occasion", "location"]
    exclude = ["order_number"]

    inlines = [OrderProductInline]
