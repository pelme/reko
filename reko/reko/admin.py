from __future__ import annotations

import typing as t
from contextvars import ContextVar
from typing import Any

import htpy as h
from django.contrib import admin, messages
from django.utils.html import format_html

from .formatters import format_percentage, format_price
from .models import (
    Order,
    OrderProduct,
    OrderQuerySet,
    Pickup,
    Producer,
    ProducerQuerySet,
    Product,
    ProductQuerySet,
    Ring,
    User,
)

if t.TYPE_CHECKING:
    from django import forms
    from django.db import models
    from django.db.models.query import QuerySet
    from django.forms import ModelForm
    from django.http import HttpRequest, HttpResponse

_current_request: ContextVar[HttpRequest] = ContextVar("request")


class RekoAdminSite(admin.AdminSite):
    site_header = "Handla REKO Admin"
    site_title = "Handla REKO Admin"
    index_title = "Admin"
    site_url = None
    enable_nav_sidebar = False


site = RekoAdminSite(name="reko")


@admin.action(description="Generera nytt lösenord")
def set_random_password(modeladmin: UserAdmin, request: HttpRequest, queryset: QuerySet[User]) -> None:
    try:
        user = queryset.get()
        password = user.set_random_password()
        user.save()
        messages.info(request, f"Nytt lösenord: {password}")

    except (User.DoesNotExist, User.MultipleObjectsReturned):
        messages.warning(request, "Välj exakt en användare att återställa lösenordet för.")


@admin.register(User, site=site)
class UserAdmin(admin.ModelAdmin[User]):
    autocomplete_fields = ["producers", "rings"]
    readonly_fields = ["last_login"]

    exclude = ["password"]
    actions = [set_random_password]

    def save_model(self, request: HttpRequest, obj: User, form: forms.Form, change: bool) -> None:
        password = obj.set_random_password()
        messages.info(request, f"Lösenord: {password}")

        super().save_model(request=request, obj=obj, form=form, change=change)


@admin.register(Producer, site=site)
class ProducerAdmin(admin.ModelAdmin[Producer]):
    list_display = ["display_name", "admin_shop_url", "phone"]
    search_fields = ["display_name"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Producer]:
        qs = super().get_queryset(request)
        assert isinstance(qs, ProducerQuerySet)
        assert isinstance(request.user, User)
        return qs.filter_by_admin(request.user)

    def changelist_view(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        _current_request.set(request)
        return super().changelist_view(request, *args, **kwargs)

    @admin.display(description="Länk")
    def admin_shop_url(self, producer: Producer) -> str:
        url = producer.get_shop_url(_current_request.get())
        return h.a(href=url)[url]  # type: ignore[return-value]


@admin.action(description="Publicera")
def make_published(modeladmin: ProductAdmin, request: HttpRequest, queryset: QuerySet[Product]) -> None:
    queryset.update(is_published=True)


@admin.action(description="Avpublicera")
def make_unpublished(modeladmin: ProductAdmin, request: HttpRequest, queryset: QuerySet[Product]) -> None:
    queryset.update(is_published=False)


@admin.register(Product, site=site)
class ProductAdmin(admin.ModelAdmin[Product]):
    actions = [make_published, make_unpublished]
    list_display = [
        "name",
        "admin_image",
        "is_published",
        "admin_price_with_vat",
    ]

    def get_queryset(self, request: HttpRequest) -> QuerySet[Product]:
        qs = super().get_queryset(request)
        assert isinstance(qs, ProductQuerySet)
        assert isinstance(request.user, User)
        return qs.filter_by_admin(request.user)

    def formfield_for_foreignkey(
        self, db_field: models.ForeignKey[t.Any, t.Any], request: HttpRequest, **kwargs: t.Any
    ) -> forms.ModelChoiceField[t.Any] | None:
        if db_field.name == "producer":
            assert isinstance(request.user, User)
            if not request.user.is_superuser:
                kwargs["queryset"] = request.user.producers.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fields(self, request: HttpRequest, obj: Product | None = None) -> tuple[str, ...]:
        user = request.user
        assert isinstance(user, User)

        base_fields = ("name", "description", "price_with_vat", "vat_factor", "image", "is_published")

        if user.is_superuser or user.producers.count() != 1:
            # Show all fields including producer
            return ("producer", *base_fields)

        # Hide producer field for users with access to single producer
        return base_fields

    def save_model(self, request: HttpRequest, obj: Product, form: ModelForm[Product], change: bool) -> None:
        assert isinstance(request.user, User)

        # Auto-set producer for users with access to only one producer
        if not obj.producer_id and not request.user.is_superuser:
            try:
                obj.producer = request.user.producers.get()
            except (Producer.DoesNotExist, Producer.MultipleObjectsReturned):
                pass

        return super().save_model(request, obj, form, change)

    @admin.display(ordering="price_with_vat", description="Pris")
    def admin_price_with_vat(self, product: Product) -> str:
        return format_price(product.price_with_vat)

    @admin.display(ordering="vat_factor", description="Momssats")
    def admin_vat_factor(self, product: Product) -> str:
        return format_percentage(product.vat_factor)

    @admin.display(description="Bild")
    def admin_image(self, producer: Producer) -> str:
        return format_html(
            '<img src="{url}" style="max-width: 100px; max-height: 100px;">',
            url=producer.image.url,
        )


class OrderProductInline(admin.TabularInline[OrderProduct, Order]):
    model = OrderProduct

    class Media:
        css = {"all": ("admin/css/hide_fk_actions.css",)}


@admin.action(description="Skicka bekräftelsemejl igen")
def send_confirmation_email(
    modeladmin: admin.ModelAdmin[Order], request: HttpRequest, queryset: QuerySet[Order]
) -> None:
    for order in queryset:
        order.confirmation_email(request).send()

    messages.info(request, "Nya bekräftelsemejl skickade.")


@admin.register(Order, site=site)
class OrderAdmin(admin.ModelAdmin[Order]):
    list_display = ["admin_order_number", "name", "admin_total_price_with_vat", "pickup"]
    list_filter = ["pickup"]
    exclude = ["order_number"]

    inlines = [OrderProductInline]
    actions = [send_confirmation_email]

    def save_model(self, request: HttpRequest, obj: Order, form: ModelForm[Order], change: bool) -> None:
        assert isinstance(request.user, User)

        # Auto-set producer for users with access to only one producer
        if not obj.producer_id and not request.user.is_superuser:
            try:
                obj.producer = request.user.producers.get()
            except (Producer.DoesNotExist, Producer.MultipleObjectsReturned):
                pass

        obj.order_number = obj.producer.generate_order_number()
        return super().save_model(request, obj, form, change)

    @admin.display(ordering="admin_total_price_with_vat", description="Summa")
    def admin_total_price_with_vat(self, order: Order) -> str:
        return format_price(order.total_price_with_vat())

    @admin.display(ordering="order_number", description="#")
    def admin_order_number(self, order: Order) -> str:
        return f"Beställning {order.order_number}"

    def get_queryset(self, request: HttpRequest) -> OrderQuerySet:
        qs = super().get_queryset(request)

        assert isinstance(qs, OrderQuerySet)
        assert isinstance(request.user, User)

        return qs.filter_by_admin(request.user)

    def formfield_for_foreignkey(
        self, db_field: models.ForeignKey[t.Any, t.Any], request: HttpRequest, **kwargs: t.Any
    ) -> forms.ModelChoiceField[t.Any] | None:
        if db_field.name == "producer":
            assert isinstance(request.user, User)
            if not request.user.is_superuser:
                kwargs["queryset"] = request.user.producers.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fields(self, request: HttpRequest, obj: Order | None = None) -> tuple[str, ...]:
        user = request.user
        assert isinstance(user, User)

        base_fields = ("pickup", "name", "email", "phone", "note")

        if user.is_superuser or user.producers.count() != 1:
            # Show all fields including producer
            return ("producer", *base_fields)

        # Hide producer field for users with access to single producer
        return base_fields


@admin.register(Pickup, site=site)
class PickupAdmin(admin.ModelAdmin[Pickup]):
    pass


@admin.register(Ring, site=site)
class RingAdmin(admin.ModelAdmin[Ring]):
    list_display = ["name"]
    search_fields = ["name"]
