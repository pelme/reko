from django.core import signing
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect

from . import components
from .cart import Cart
from .forms import OrderForm, OrderProductForms
from .models import Order, OrderProduct, Producer


def index(request: HttpRequest) -> HttpResponse:
    return redirect("/admin/")


def producer_index(request: HttpRequest, producer_slug: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)
    cart = Cart.from_request_cookie(producer, request)
    return HttpResponse(
        components.producer_index(
            request=request,
            producer=producer,
            cart=cart,
        )
    )


def product_cart_update(request: HttpRequest, producer_slug: str, product_id: int) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)
    cart = Cart.from_request_cookie(producer, request)
    product = producer.product_set.get(id=product_id)

    count_str = request.POST.get("count", "")
    if not count_str:
        return HttpResponseBadRequest("Missing count.")

    try:
        count = int(count_str)
    except ValueError:
        return HttpResponseBadRequest("Invalid count.")

    if count_str == "+1":
        updated_cart = cart.new_count(product, cart.get_count(product) + 1)
    elif count_str == "-1":
        updated_cart = cart.new_count(product, cart.get_count(product) - 1)
    else:
        updated_cart = cart.new_count(product, count)

    response = HttpResponse(
        components.producer_index(
            request=request,
            producer=producer,
            cart=updated_cart,
        )
    )
    updated_cart.set_response_cookie(response)
    return response


def order(request: HttpRequest, producer_slug: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)

    form_data = request.POST or None
    order_form = OrderForm(form_data, locations=producer.location_set.all())
    product_forms = OrderProductForms(producer, form_data)

    if order_form.is_valid() and product_forms.is_valid():
        order = Order.objects.create(
            producer=producer,
            name=order_form.cleaned_data["name"],
            order_number=producer.generate_order_number(),
        )

        OrderProduct.objects.bulk_create(
            [
                OrderProduct(
                    order=order,
                    product=product,
                    amount=amount,
                    price=product.price,
                )
                for product, form in product_forms.form_list
                if (amount := (form.cleaned_data["amount"] or 0)) > 0
            ]
        )

        return redirect("order-summary", signing.dumps(str(order.id)))

    return HttpResponse(
        components.order(
            request=request,
            producer=producer,
            order_form=order_form,
            product_forms=product_forms,
        )
    )