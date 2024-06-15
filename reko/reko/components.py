import htpy as h
from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.template.backends.utils import csrf_input
from django.templatetags.static import static
from django.urls import reverse

from .cart import Cart
from .format_price import format_price
from .forms import OrderForm, ProductCartForm, ProductCartForms, SubmitWidget
from .models import Order, Producer


def base(*, request: HttpRequest, title: str, logo_url: str, content: h.Node, cart: h.Node = None) -> h.Element:
    return h.html(".sl-theme-light", lang="sv")[
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
                href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.0/cdn/themes/light.css",
            ),
            h.link(
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.0/cdn/themes/dark.css",
            ),
            h.script(
                type="module",
                src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.15.0/cdn/shoelace-autoloader.js",
            ),
        ],
        h.body(hx_headers='{"X-CSRFToken": "%s"}' % get_token(request))[
            h.header[
                h.div(".content")[
                    h.a(href=logo_url)[h.img(".logo", src=static("reko/logo.png"), alt="Rekoplus logo")],
                    cart,
                ],
            ],
            h.main[content],
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
                h.sl_icon(name="bag", label="Varukorg"),
                f"{cart.total_count()} varor, {format_price(cart.total_price())}",
            ]
            if cart
            else None
        ),
    )


def cart_update_button(*, icon: str, label: str, action: str) -> h.Element:
    return h.sl_tooltip(content=label)[
        h.sl_button(type="submit", name="plus", value="1", circle=True)[h.sl_icon(name=icon)]
    ]


def product_card(url: str, form: ProductCartForm) -> h.Element:
    product = form.product

    current_count = form.initial.get("count", 0)

    return h.sl_card(".product")[
        h.img(slot="image", loading="lazy", src=str(product.card_thumbnail.url), alt=product.name, height="150"),
        h.div(".name-and-price")[
            h.a(href="#")[h.h3[product.name]],
            h.span[format_price(product.price)],
        ],
        h.p(".description")[product.description],
        h.form(hx_post=url, hx_trigger="sl-change,submit,change", hx_target="body")[
            (
                form["plus"].as_widget(
                    SubmitWidget(
                        [
                            h.sl_icon(
                                name="plus-lg",
                                slot="prefix",
                            ),
                            "Lägg till i varukorg",
                        ],
                        class_="buy",
                    )
                ),
            )
            if not current_count
            else [
                h.sl_tooltip(content="Ta bort en vara")[form["minus"].as_widget(SubmitWidget("-", pill=True))],
                form["count"],
                h.sl_tooltip(content="Lägg till ytterligare")[form["plus"].as_widget(SubmitWidget("+", pill=True))],
            ]
        ],
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
            h.section(".products")[
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
                h.table[
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
                            order_form.as_ul(),
                            h.li[h.button(type="submit", class_="submit")["Beställ!"]],
                        ],
                    ],
                ],
            ],
        ),
    )


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
