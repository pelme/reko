import htpy as h
from django.forms import BoundField
from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.template.backends.utils import csrf_input
from django.templatetags.static import static
from django.urls import reverse

from .cart import Cart
from .formatters import format_amount, format_price
from .forms import OrderForm, ProductCartForm, ProductCartForms, SubmitWidget
from .models import Order, Producer


def base(*, request: HttpRequest, title: str, logo_url: str, content: h.Node, cart: h.Node = None) -> h.Element:
    return h.html(lang="sv")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(
                name="viewport",
                content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover",
            ),
            h.title[f"{title} - Rekoplus"],
            h.style[
                # Avoid Flash of Undefined Custom Elements (FOUCE):
                # https://www.abeautifulsite.net/posts/flash-of-undefined-custom-elements/
                ":not(:defined) { visibility: hidden; }"
            ],
            h.link(rel="stylesheet", href=static("reko/reko.css")),
            h.link(rel="shortcut icon", href=static("reko/favicon.webp")),
            h.script(defer=True, src=static("vendor/alpinejs.min.js")),
            h.script(defer=True, src=static("vendor/htmx.min.js")),
            h.link(
                rel="stylesheet",
                href=static("vendor/pico.green.min.css"),
            ),
        ],
        h.body(hx_headers='{"X-CSRFToken": "%s"}' % get_token(request))[
            h.header[
                h.div(".container")[
                    h.a(href=logo_url)[h.img(".logo", src=static("reko/logo.png"), alt="Rekoplus logo")],
                    cart,
                ],
            ],
            h.main(".container")[content],
            h.footer[
                h.ul[
                    h.a(href="/")[h.li["Om rekoplus.se"]],
                    h.a(href="#")[h.li["Bli en försäljare"]],
                    h.a(href="#")[h.li["Kontakt"]],
                ],
            ],
        ],
    ]


def producer_base(
    *, request: HttpRequest, producer: Producer, title: str = "", content: h.Node, cart: Cart | None = None
) -> h.Element:
    return base(
        request=request,
        title=(f"{title} - " if title else "") + producer.name,
        content=content,
        logo_url=reverse("producer-index", args=[producer.slug]),
        cart=(
            h.a(".cart", href=reverse("order", args=[producer.slug]))[
                basket_icon(),
                f"{cart.total_count()} varor, {format_price(cart.total_price())}",
            ]
            if cart
            else None
        ),
    )


def product_card(url: str, form: ProductCartForm) -> h.Element:
    product = form.product

    current_count = form.initial.get("count", 0)

    return h.a(href="#")[
        h.article(".product")[
            h.header[
                h.figure(style=("border-radius: var(--pico-border-radius);" "overflow: hidden;"))[
                    h.img(
                        slot="image",
                        loading="lazy",
                        src=str(product.card_thumbnail.url),
                        alt=product.name,
                        height="150",
                    ),
                ],
                h.h4[product.name],
            ],
            h.p(".description")[product.description],
            h.footer[
                h.span[format_price(product.price)],
                h.form(
                    role="group",
                    hx_post=url,
                    hx_trigger="submit,change",
                    hx_target="body",
                )[
                    (form["plus"].as_widget(SubmitWidget("+ Lägg till", class_="buy")),)
                    if not current_count
                    else [
                        form["minus"].as_widget(SubmitWidget("-")),
                        h.span(".current-count")[str(current_count)],
                        form["plus"].as_widget(SubmitWidget("+")),
                    ]
                ],
            ],
        ]
    ]


def producer_index(
    request: HttpRequest, producer: Producer, product_cart_forms: ProductCartForms, cart: Cart
) -> h.Element:
    upcoming_locations = list(producer.get_upcoming_locations())
    return producer_base(
        request=request,
        producer=producer,
        cart=cart,
        content=(
            h.section(".introduction")[
                h.h1[producer.name],
                (
                    [
                        h.h2["Kommande utlämningar"],
                        h.ul[(h.li[f"{location.date}: {location.place_and_time}"] for location in upcoming_locations)],
                    ]
                    if upcoming_locations
                    else h.p["Inga utlämningar planerade just nu."]
                ),
                h.p[producer.description],
            ],
            h.section(".products-grid")[
                (product_card(request.path, product_cart_form) for product_cart_form in product_cart_forms.forms)
            ],
        ),
    )


def order(
    request: HttpRequest,
    producer: Producer,
    order_form: OrderForm,
    cart: Cart,
    product_cart_forms: ProductCartForms,
) -> h.Element:
    return producer_base(
        request=request,
        producer=producer,
        title="Beställning",
        cart=cart,
        content=(
            h.section(".introduction")[
                h.h1[producer.name],
                h.h2["Beställ dina varor"],
            ],
            h.form(method="post")[
                csrf_input(request),
                h.table(".striped")[
                    h.thead[
                        h.tr[
                            h.th["Produkt"],
                            h.th["Pris"],
                            h.th["Antal"],
                            h.th["Summa"],
                        ]
                    ],
                    h.tbody[
                        (
                            h.tr[
                                h.td[form.product.name],
                                h.td[format_price(form.product.price)],
                                h.td[form["count"]],
                                h.td[format_price(form.product.price * form.initial.get("count", 0))],
                            ]
                            for form in product_cart_forms.forms
                            if form.initial.get("count", 0)
                        )
                    ],
                ],
                h.div[
                    h.h2["Dina uppgifter"],
                    h.ul[
                        h.div(".form")[
                            _render_field(order_form["name"]),
                            _render_field(order_form["email"]),
                            _render_field(order_form["phone"]),
                            _render_field(order_form["location"]),
                            _render_field(order_form["note"]),
                            h.button(type="submit", class_="submit")["Beställ!"],
                        ],
                    ],
                ],
            ],
        ),
    )


def _render_field(form_field: BoundField) -> h.Element:
    return h.label[
        form_field.label,
        form_field,
        h.div(".error-message")[form_field.errors],
    ]


def order_summary(*, request: HttpRequest, producer: Producer, order: Order) -> h.Element:
    return producer_base(
        request=request,
        title="Tack för din beställning!",
        producer=producer,
        content=h.section(".introduction")[
            h.h1["Tack för din beställning!"],
            h.dl[
                h.dt["Ordernummer"],
                h.dd[f"{order.order_number}"],
                h.dt["Datum"],
                h.dt[order.location.date.strftime("%Y-%m-%d")],
                h.dt["Utlämningsplats"],
                h.dd[order.location.place_and_time],
            ],
        ],
    )


def basket_icon() -> h.Element:
    # https://icons.getbootstrap.com/icons/basket/
    return h.svg(
        ".bi.bi-basket",
        xmlns="http://www.w3.org/2000/svg",
        width="16",
        height="16",
        fill="currentColor",
        viewbox="0 0 16 16",
    )[
        h.path(
            d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1v4.5a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 1 13.5V9a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h1.217L5.07 1.243a.5.5 0 0 1 .686-.172zM2 9v4.5A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5V9zM1 7v1h14V7zm3 3a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3A.5.5 0 0 1 4 10m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3A.5.5 0 0 1 6 10m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3A.5.5 0 0 1 8 10m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3a.5.5 0 0 1 .5-.5m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3a.5.5 0 0 1 .5-.5"  # noqa
        )
    ]
