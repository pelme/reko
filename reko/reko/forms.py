from __future__ import annotations

import typing as t

import htpy as h
from django import forms
from django.utils.safestring import SafeString

if t.TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.forms.renderers import BaseRenderer
    from django.http import QueryDict

    from .cart import Cart
    from .models import Pickup, Product


class ProductCartForms:
    def __init__(self, *, data: QueryDict | None, cart: Cart, products: list[Product]) -> None:
        self.data = data
        self.cart = cart
        self.forms = [
            ProductCartForm(data, product=product, initial_count=cart.get_count(product)) for product in products
        ]

    def get_updated_cart(
        self,
    ) -> Cart:
        if self.data is None:
            return self.cart

        cart = self.cart

        for form in self.forms:
            if form.is_valid():
                cart = form.get_updated_cart(cart)

        return cart


class SubmitWidget(forms.Widget):
    def __init__(self, contents: h.Node, **attrs: t.Any) -> None:
        super().__init__(attrs)
        self.contents = contents

    def render(
        self, name: str, value: str, attrs: dict[str, str] | None = None, renderer: BaseRenderer | None = None
    ) -> SafeString:
        all_attrs = {**self.attrs, **(attrs or {})}
        return SafeString(
            str(
                h.button(
                    ".wa-brand",
                    type="submit",
                    name=name,
                    value="1",
                    **all_attrs,
                )[self.contents]
            )
        )


class ProductCartForm(forms.Form):
    plus = forms.BooleanField(required=False)
    minus = forms.BooleanField(required=False)
    count = forms.IntegerField(
        min_value=0,
        required=False,
        widget=forms.TextInput(attrs={"inputmode": "numeric"}),
    )

    def __init__(self, *args: t.Any, product: Product, initial_count: int, **kwargs: t.Any) -> None:
        self.product = product

        kwargs["prefix"] = str(product.id)
        kwargs["initial"] = {"count": initial_count}
        super().__init__(*args, **kwargs)

    def get_updated_cart(self, cart: Cart) -> Cart:
        assert self.is_valid()
        current_count = cart.get_count(self.product)

        if self.cleaned_data.get("plus"):
            return cart.with_new_count(self.product, current_count + 1)

        if self.cleaned_data.get("minus"):
            return cart.with_new_count(self.product, current_count - 1)

        if (count := self.cleaned_data.get("count")) is not None:
            return cart.with_new_count(self.product, count)

        return cart


class OrderForm(forms.Form):
    name = forms.CharField(
        label="Namn",
        widget=forms.TextInput(
            attrs={
                "autocomplete": "name",
                "placeholder": "Anna Andersson",
            }
        ),
    )
    email = forms.EmailField(
        label="Mejladress",
        widget=forms.EmailInput(
            attrs={
                "autocomplete": "email",
                "placeholder": "din.epost@example.com",
            }
        ),
    )
    phone = forms.CharField(
        label="Mobiltelefon",
        widget=forms.TextInput(
            attrs={
                "type": "tel",
                "autocomplete": "tel",
                "placeholder": "070-123 45 67",
            }
        ),
    )
    note = forms.CharField(
        label="Övriga kommentarer (valfritt)",
        required=False,
        widget=forms.Textarea(
            attrs={
                "autocomplete": "off",
                "rows": 2,
                "placeholder": "Om du har några särskilda önskemål, skriv gärna här...",
            }
        ),
    )

    def __init__(self, *args: t.Any, pickups: QuerySet[Pickup], **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["pickup"] = forms.ModelChoiceField(
            label="Utlämningsplats",
            queryset=pickups,
            empty_label="-- Välj utlämningsplats --",
        )
