from __future__ import annotations
from typing import TYPE_CHECKING
from django.db.models import QuerySet
from django import forms

from .models import Order

if TYPE_CHECKING:
    from reko.occassion.models import Location


class OrderProductForm(forms.Form):
    amount = forms.IntegerField(
        initial=0, min_value=0, required=False, widget=forms.TextInput
    )


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["first_name", "last_name", "email", "note", "location"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Förnamn"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Efternamn"}),
        }

    def __init__(self, *args, locations: QuerySet[Location], **kwargs):
        super().__init__(
            *args,
            initial={
                "first_name": "Andreas",
                "last_name": "Pelme",
                "email": "andreas@pelme.se",
            },
            **kwargs
        )
        self.fields["location"].queryset = locations
