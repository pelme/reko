from contextvars import ContextVar
from typing import Any

import htpy as h
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.utils.html import format_html

from .formatters import format_price
from .models import Order, OrderProduct, Producer, Product

_current_request: ContextVar[HttpRequest] = ContextVar("request")


class RekoAdminSite(admin.AdminSite):
    site_header = "Rekoplus Admin"
    site_title = "Rekoplus Admin"
    index_title = "Admin"
    site_url = None


site = RekoAdminSite(name="reko")


@admin.register(Producer, site=site)
class ProducerAdmin(admin.ModelAdmin[Producer]):
    list_display = ["name", "admin_shop_url", "phone"]

    def changelist_view(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        _current_request.set(request)
        return super().changelist_view(request, *args, **kwargs)

    @admin.display(description="URL")
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


@admin.register(Order, site=site)
class OrderAdmin(admin.ModelAdmin[Order]):
    list_display = ["order_number", "name", "total_price"]
    list_filter = ["location"]
    exclude = ["order_number"]

    inlines = [OrderProductInline]
