from django.contrib import admin

from .models import Order, OrderProduct


class OrderProductInline(admin.TabularInline[OrderProduct, Order]):
    model = OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin[Order]):
    list_display = ["full_order_number", "full_name", "total_price"]
    list_filter = ["occasion", "location"]
    exclude = ["order_number"]

    inlines = [OrderProductInline]
