from django.core import signing
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from reko.occasion.models import Occasion
from reko.producer.models import Producer, Product

from .forms import OrderForm, OrderProductForm
from .models import Order, OrderProduct


class _OrderProductForms:
    form_list: list[tuple[Product, OrderProductForm]]

    def __init__(self, request: HttpRequest, producer: Producer) -> None:
        products = producer.product_set.all()

        self.list = [
            (product, OrderProductForm(request.POST or None, prefix=str(product.id)))
            for product in products
        ]

    def is_valid(self) -> bool:
        return all(form.is_valid() for form in self.forms)

    @property
    def forms(self) -> list[OrderProductForm]:
        return [form for _product, form in self.list]


def order_products(request: HttpRequest, producer_slug: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)

    return render(
        request,
        "partials/order_products.html",
        {"product_forms": _OrderProductForms(request, producer)},
    )


def order(request: HttpRequest, producer_slug: str) -> HttpResponse:
    occasion = Occasion.objects.get()
    producer = get_object_or_404(Producer, slug=producer_slug)

    order_form = OrderForm(request.POST or None, locations=occasion.locations.all())
    product_forms = _OrderProductForms(request, producer)

    if order_form.is_valid() and product_forms.is_valid():
        order = order_form.save(commit=False)
        order.producer = producer
        order.occasion = occasion
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
            "occasion": occasion,
            "order_form": order_form,
            "product_forms": product_forms,
        },
    )


def order_summary(request: HttpRequest, signed_order_id: str) -> HttpResponse:
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
            "occasion": order.occasion,
            "location": order.location,
        },
    )
