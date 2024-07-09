from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

from . import components
from .cart import Cart
from .forms import OrderForm, ProductCartForms
from .models import Order, OrderProduct, Producer


def index(request: HttpRequest) -> HttpResponse:
    return redirect("/admin/")


def producer_index(request: HttpRequest, producer_slug: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)
    initial_cart = Cart.from_cookie(producer, request)

    products = list(producer.product_set.filter(is_published=True))

    product_cart_forms = ProductCartForms(data=request.POST or None, cart=initial_cart, products=products)
    cart = product_cart_forms.get_updated_cart()

    response = HttpResponse(
        components.producer_index(
            request=request,
            producer=producer,
            cart=cart,
            product_cart_forms=ProductCartForms(data=None, cart=cart, products=products),
        )
    )

    cart.set_cookie(response)
    return response


def order(request: HttpRequest, producer_slug: str) -> HttpResponse:
    response: HttpResponse
    producer = get_object_or_404(Producer, slug=producer_slug)

    is_refresh = bool(request.POST.get("refresh"))
    is_submit = request.method == "POST" and not is_refresh
    form_data = request.POST or None
    order_form = OrderForm(form_data, locations=producer.location_set.all())
    initial_cart = Cart.from_cookie(producer, request)
    product_cart_forms = ProductCartForms(
        data=request.POST or None,
        cart=initial_cart,
        products=list(initial_cart.items.keys()),
    )

    cart = product_cart_forms.get_updated_cart()

    if is_submit and order_form.is_valid() and product_cart_forms.is_valid():
        order = Order.objects.create(
            producer=producer,
            order_number=producer.generate_order_number(),
            name=order_form.cleaned_data["name"],
            phone=order_form.cleaned_data["phone"],
            email=order_form.cleaned_data["email"],
            location=order_form.cleaned_data["location"],
            note=order_form.cleaned_data["note"],
        )

        OrderProduct.objects.bulk_create(
            [
                OrderProduct(
                    order=order,
                    product=product,
                    name=product.name,
                    amount=count,
                    price=product.price,
                )
                for product, count in cart.items.items()
            ]
        )

        response = redirect(
            "order-summary",
            producer_slug=producer.slug,
            order_secret=order.order_secret(),
        )
        Cart.empty(producer).set_cookie(response)
        return response

    response = HttpResponse(
        components.order(
            request=request,
            cart=cart,
            producer=producer,
            order_form=order_form,
            product_cart_forms=product_cart_forms,
        )
    )
    cart.set_cookie(response)
    return response


def order_summary(request: HttpRequest, producer_slug: str, order_secret: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)
    order: Order = get_object_or_404(Order.objects.filter_order_secret(producer, order_secret))

    return HttpResponse(
        components.order_summary(
            request=request,
            order=order,
            producer=producer,
        )
    )
