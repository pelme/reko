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
    from .models import Location, Product


class ProductCartForms:
    def __init__(self, *, data: QueryDict | None, cart: Cart, products: list[Product]) -> None:
        self.data = data
        self.cart = cart
        self.forms = [
            ProductCartForm(data, product=product, initial_count=cart.get_count(product)) for product in products
        ]

    def is_valid(self) -> bool:
        return all(form.is_valid() for form in self.forms)

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
    count = forms.IntegerField(min_value=0, required=False)

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
    name = forms.CharField(label="Namn", widget=forms.TextInput(attrs={"placeholder": "Namn"}), initial="Andreas")
    email = forms.EmailField(label="Mejladress", initial="andreas@pelme.se")
    phone = forms.CharField(label="Mobiltelefon", initial="0704773720")
    note = forms.CharField(label="Övrigt", required=False, widget=forms.Textarea, initial="Gott med tomater!")

    def __init__(self, *args: t.Any, locations: QuerySet[Location], **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["location"] = forms.ModelChoiceField(label="Utlämningsplats", queryset=locations)
