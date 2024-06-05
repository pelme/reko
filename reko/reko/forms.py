from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django import forms

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import QueryDict

    from .models import Location, Producer, Product


class OrderProductForm(forms.Form):
    amount = forms.IntegerField(initial=0, min_value=0, required=False, widget=forms.TextInput)


class OrderForm(forms.Form):
    # the same fields as in the Order model with nice placeholders
    first_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Förnamn"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Efternamn"}))
    email = forms.EmailField()
    phone = forms.CharField()
    note = forms.CharField(required=False, widget=forms.Textarea)

    def __init__(self, *args: Any, locations: QuerySet[Location], **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["location"] = forms.ModelChoiceField(queryset=locations)


class OrderProductForms:
    def __init__(self, producer: Producer, form_data: QueryDict | None) -> None:
        products = producer.product_set.all()

        self.form_list: list[tuple[Product, OrderProductForm]] = [
            (product, OrderProductForm(form_data, prefix=str(product.id))) for product in products
        ]

    def is_valid(self) -> bool:
        return all(form.is_valid() for form in self.forms)

    @property
    def forms(self) -> list[OrderProductForm]:
        return [form for _product, form in self.form_list]
