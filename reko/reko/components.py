import htpy as h
from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.templatetags.static import static
from django.urls import reverse

from .cart import Cart
from .format_price import format_price
from .forms import OrderForm, OrderProductForms
from .models import Producer, Product


def base(*, request: HttpRequest, title: str, content: h.Node, cart: h.Node = None) -> h.Element:
    return h.html(".sl-theme-light", lang="sv")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(
                name="viewport",
                content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover",
            ),
            h.title[f"{title} - Rekoplus"],
            h.style[
                """
				/*
                Avoid Flash of Undefined Custom Elements (FOUCE):
                https://www.abeautifulsite.net/posts/flash-of-undefined-custom-elements/
                */
                :not(:defined) {
                    visibility: hidden;
                }
                """
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
                    h.img(".logo", src=static("reko/logo.png"), alt="Rekoplus logo"),
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


def product_card(product: Product, current_count: int) -> h.Element:
    return h.sl_card(".product", hx_target="body")[
        h.img(slot="image", loading="lazy", src=str(product.card_thumbnail.url), alt=product.name, height="150"),
        h.div(".name-and-price")[
            h.a(href="#")[h.h3[product.name]],
            h.span[format_price(product.price)],
        ],
        h.p(".description")[product.description],
        (
            h.sl_button(
                ".buy",
                variant="primary",
                outline=True,
                hx_post=reverse("cart-add", args=[product.producer.slug, product.id]),
            )[
                h.sl_icon(
                    name="bag-plus",
                    slot="prefix",
                ),
                "Lägg i varukorg",
                f" (i varukorgen: {current_count})" if current_count else "",
            ]
        )
        if not current_count
        else [
            h.sl_button(hx_post=reverse("cart-add", args=[product.producer.slug, product.id]))["PLUS"],
            f"Antal: {current_count}",
            h.sl_button(hx_post=reverse("cart-decrease", args=[product.producer.slug, product.id]))["MINUS"],
        ],
    ]


def producer_index(request: HttpRequest, producer: Producer, cart: Cart) -> h.Element:
    upcoming_locations = list(producer.get_upcoming_locations())
    return base(
        request=request,
        title=producer.name,
        cart=(
            h.a(".cart", href=reverse("order", args=[producer.slug]))[
                h.sl_icon(name="bag", label="Varukorg"),
                f"{cart.total_count()} varor, {format_price(cart.total_price())}",
            ],
        ),
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
                (
                    product_card(product, current_count=cart.get_count(product))
                    for product in producer.product_set.filter(is_published=True)
                )
            ],
        ),
    )


def order(
    request: HttpRequest, producer: Producer, order_form: OrderForm, product_forms: OrderProductForms
) -> h.Element:
    return base(
        request=request,
        title=f"{producer.name} - Beställning",
        content=(
            h.section(".introduction")[
                h.h1[producer.name],
                h.h2["Beställ dina varor"],
            ],
        ),
    )
