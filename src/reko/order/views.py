from typing import TYPE_CHECKING

from django.http import HttpRequest, HttpResponse
from django.http import Http404
from django.shortcuts import get_object_or_404, render, redirect

from reko.occassion.models import Occassion
from django.core import signing
from reko.producer.models import Producer

from .models import Order
from .forms import OrderForm, OrderProductForm
from .models import OrderProduct

if TYPE_CHECKING:
    from reko.producer.models import Product


class _OrderProductForms:
    def __init__(self, request, producer):
        products = producer.product_set.all()

        self.list: list[tuple[Product, OrderProductForm]] = [
            (product, OrderProductForm(request.POST or None, prefix=product.id))
            for product in products
        ]

    def is_valid(self):
        return all(form.is_valid() for form in self.forms)

    @property
    def forms(self):
        return [form for product, form in self.list]


def order_products(request: HttpRequest, producer_slug: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)

    return render(
        "partials/order_products.html",
        {"product_forms": _OrderProductForms(request, producer)},
    )


def order(request: HttpRequest, producer_slug: str) -> HttpResponse:
    occassion = Occassion.objects.get()
    producer = get_object_or_404(Producer, slug=producer_slug)

    order_form = OrderForm(request.POST or None, locations=occassion.locations.all())
    product_forms = _OrderProductForms(request, producer)

    if order_form.is_valid() and product_forms.is_valid():
        order = order_form.save(commit=False)
        order.producer = producer
        order.occassion = occassion
        order.generate_order_number()
        order.save()

        OrderProduct.objects.bulk_create(
            [
                OrderProduct(
                    order=order, product=product, amount=amount, price=product.price
                )
                for product, form in product_forms.list
                if (amount := (form.cleaned_data["amount"] or 0)) > 0
            ]
        )

        return redirect("order-summary", signing.dumps(str(order.id)))

    return render(
        request,
        "order.html",
        {
            "producer": producer,
            "occassion": occassion,
            "order_form": order_form,
            "product_forms": product_forms,
        },
    )


def order_summary(request, signed_order_id):
    try:
        order_id = signing.loads(signed_order_id)
    except signing.BadSignature:
        raise Http404

    order = get_object_or_404(Order, id=order_id)

    return render(
        request,
        "order_summary.html",
        {
            "order": order,
            "occassion": order.occassion,
            "location": order.location,
        },
    )
