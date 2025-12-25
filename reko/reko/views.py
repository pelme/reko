from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from . import components
from .cart import Cart
from .forms import OrderForm, ProductCartForms
from .models import Order, OrderProduct, Producer


def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse(str(components.index_page(request=request)))


def about(request: HttpRequest) -> HttpResponse:
    return HttpResponse(
        str(
            components.static_content(
                request=request,
                title="Om oss",
                markdown_file="about.md",
            )
        )
    )


def producer_index(request: HttpRequest, producer_slug: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)
    initial_cart = Cart.from_cookie(producer, request)

    products = list(producer.product_set.filter(is_published=True))

    product_cart_forms = ProductCartForms(data=request.POST or None, cart=initial_cart, products=products)
    cart = product_cart_forms.get_updated_cart()

    response = HttpResponse(
        str(
            components.producer_index(
                request=request,
                producer=producer,
                cart=cart,
                product_cart_forms=ProductCartForms(data=None, cart=cart, products=products),
            )
        )
    )

    cart.set_cookie(response)
    return response


def order(request: HttpRequest, producer_slug: str) -> HttpResponse:
    response: HttpResponse
    producer = get_object_or_404(Producer, slug=producer_slug)

    is_submit = request.method == "POST"
    form_data = request.POST or None
    order_form = OrderForm(form_data, pickup_locations=producer.get_upcoming_pickup_locations())
    cart = Cart.from_cookie(producer, request)

    if is_submit and order_form.is_valid():
        order = Order.objects.create(
            producer=producer,
            order_number=producer.generate_order_number(),
            name=order_form.cleaned_data["name"],
            phone=order_form.cleaned_data["phone"],
            email=order_form.cleaned_data["email"],
            pickup_location=order_form.cleaned_data["pickup_location"],
            note=order_form.cleaned_data["note"],
        )

        assert cart.total_count() > 0
        OrderProduct.objects.bulk_create(
            [
                OrderProduct(
                    order=order,
                    product=product,
                    name=product.name,
                    amount=count,
                    price_with_vat=product.price_with_vat,
                    vat_factor=product.vat_factor,
                )
                for product, count in cart.items.items()
            ]
        )

        order.confirmation_email(request).send(fail_silently=True)

        response = HttpResponseRedirect(order.order_summary_url(request))
        Cart.empty(producer).set_cookie(response)
        return response

    response = HttpResponse(
        components.order(
            request=request,
            cart=cart,
            producer=producer,
            order_form=order_form,
        )
    )
    return response


def order_summary(request: HttpRequest, producer_slug: str, order_secret: str) -> HttpResponse:
    producer = get_object_or_404(Producer, slug=producer_slug)
    order: Order = get_object_or_404(Order.objects.filter_order_secret(producer, order_secret))

    # Debug helper: View the contents of the email by adding ?mail to a order summary url
    if "mail" in request.GET:
        return HttpResponse(
            str(
                components.order_confirmation_email(
                    order=order,
                    request=request,
                )
            )
        )

    return HttpResponse(
        str(
            components.order_summary(
                request=request,
                order=order,
            )
        )
    )
