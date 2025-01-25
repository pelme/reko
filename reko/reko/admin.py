from contextvars import ContextVar
from typing import Any

import htpy as h
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse
from django.utils.html import format_html

from .formatters import format_price
from .models import Order, OrderProduct, Producer, Product, Ring

_current_request: ContextVar[HttpRequest] = ContextVar("request")


class RekoAdminSite(admin.AdminSite):
    site_header = "Handla REKO Admin"
    site_title = "Handla REKO Admin"
    index_title = "Admin"
    site_url = None
    enable_nav_sidebar = False


site = RekoAdminSite(name="reko")


@admin.register(Producer, site=site)
class ProducerAdmin(admin.ModelAdmin[Producer]):
    list_display = ["display_name", "admin_shop_url", "phone"]

    def changelist_view(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        _current_request.set(request)
        return super().changelist_view(request, *args, **kwargs)

    @admin.display(description="Länk")
    def admin_shop_url(self, producer: Producer) -> str:
        url = producer.get_shop_url(_current_request.get())
        return h.a(href=url)[url]  # type: ignore[return-value]


@admin.action(description="Publicera")
def make_published(modeladmin: ProducerAdmin, request: HttpRequest, queryset: QuerySet[Product]) -> None:
    queryset.update(is_published=True)


@admin.action(description="Avpublicera")
def make_unpublished(modeladmin: ProducerAdmin, request: HttpRequest, queryset: QuerySet[Product]) -> None:
    queryset.update(is_published=False)


@admin.register(Product, site=site)
class ProductAdmin(admin.ModelAdmin[Product]):
    actions = [make_published, make_unpublished]
    list_display = [
        "name",
        "admin_image",
        "is_published",
        "admin_price",
    ]

    @admin.display(ordering="price", description="Pris")
    def admin_price(self, product: Product) -> str:
        return format_price(product.price)

    @admin.display(description="Bild")
    def admin_image(self, producer: Producer) -> str:
        return format_html(
            '<img src="{url}" style="max-width: 100px; max-height: 100px;">',
            url=producer.image.url,
        )


class OrderProductInline(admin.TabularInline[OrderProduct, Order]):
    model = OrderProduct


@admin.action(description="Skicka bekräftelsemejl igen")
def send_confirmation_email(
    modeladmin: admin.ModelAdmin[Order], request: HttpRequest, queryset: QuerySet[Order]
) -> None:
    for order in queryset:
        order.confirmation_email(request).send()

    messages.info(request, "Nya bekräftelsemejl skickade.")


@admin.register(Order, site=site)
class OrderAdmin(admin.ModelAdmin[Order]):
    list_display = ["admin_order_number", "name", "admin_total_price", "pickup"]
    list_filter = ["pickup"]
    exclude = ["order_number"]

    inlines = [OrderProductInline]
    actions = [send_confirmation_email]

    def save_model(self, request: HttpRequest, obj: Order, form: ModelForm[Order], change: bool) -> None:
        obj.order_number = obj.producer.generate_order_number()
        return super().save_model(request, obj, form, change)

    @admin.display(ordering="total_price", description="Summa")
    def admin_total_price(self, order: Order) -> str:
        return format_price(order.total_price())

    @admin.display(ordering="order_number", description="#")
    def admin_order_number(self, order: Order) -> str:
        return f"Beställning {order.order_number}"


@admin.register(Ring, site=site)
class RingAdmin(admin.ModelAdmin[Ring]):
    list_display = ["name"]
    search_fields = ["name"]
