import datetime
from collections import defaultdict

import htpy as h
from django.forms import BoundField
from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.template.backends.utils import csrf_input
from django.template.defaultfilters import pluralize
from django.templatetags.static import static
from django.urls import reverse
from django.utils import formats

from .cart import Cart
from .formatters import format_amount, format_price, format_time_range
from .forms import OrderForm, ProductCartForm, ProductCartForms, SubmitWidget
from .models import Order, Pickup, Producer


@h.with_children
def base(
    content: h.Node,
    *,
    request: HttpRequest,
    title: str,
    brand_color: str = "gray",
) -> h.Element:
    return h.html(lang="sv", class_=f"wa-theme-default wa-brand-{brand_color}")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(
                name="viewport", content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover"
            ),
            h.title[f"{title} - Handla REKO"],
            h.style[
                # Avoid Flash of Undefined Custom Elements (FOUCE):
                # https://www.abeautifulsite.net/posts/flash-of-undefined-custom-elements/
                ":not(:defined) { visibility: hidden; }"
            ],
            h.link(
                rel="stylesheet", href="https://early.webawesome.com/webawesome@3.0.0-beta.4/dist/styles/webawesome.css"
            ),
            h.link(
                rel="stylesheet",
                href="https://early.webawesome.com/webawesome@3.0.0-beta.4/dist/styles/themes/default.css",
            ),
            h.script(
                type="module", src="https://early.webawesome.com/webawesome@3.0.0-beta.4/dist/webawesome.loader.js"
            ),
            h.link(rel="stylesheet", href=static("reko/reko.css")),
            h.link(rel="shortcut icon", href=static("reko/favicon.webp")),
            h.script(defer=True, src=static("vendor/alpinejs.min.js")),
            h.script(defer=True, src=static("vendor/htmx.min.js")),
            h.script(defer=True, src=static("vendor/multi-swap.js")),
        ],
        h.body(hx_headers=f'{{"X-CSRFToken": "{get_token(request)}"}}', hx_ext="multi-swap")[
            [
                content,
                h.footer[
                    h.hr,
                    h.section(".wa-cluster.wa-gap-xl")[
                        h.a(href="/")["Om handlareko.se"],
                        h.a(href="#")["Bli en försäljare"],
                        h.a(href="#")["Kontakt"],
                    ],
                ],
            ]
        ],
    ]


@h.with_children
def producer_base(
    content: h.Node,
    *,
    request: HttpRequest,
    producer: Producer,
    title: str = "",
) -> h.Element:
    return base(
        request=request,
        title=(f"{title} - " if title else "") + producer.display_name,
        brand_color=producer.color_palette,
    )[content]


def product_card(url: str, form: ProductCartForm) -> h.Element:
    product = form.product

    current_count = form.initial.get("count", 0)

    form_id = f"product-form-{product.id}"

    return h.wa_card(".product-card")[
        h.img(
            slot="media",
            loading="lazy",
            src=str(product.card_thumbnail.url),
            alt=product.name,
            height="150",
        ),
        h.div[
            h.div(".wa-flank.wa-flank:end.wa-align-items-start.wa-heading-m")[
                h.h4[product.name],
                h.span[format_price(product.price)],
            ],
            h.p(style="flex: 1")[product.description],
        ],
        h.form(
            f"#{form_id}",
            slot="footer",
            role="group",
            hx_post=url,
            hx_trigger="submit,change",
            hx_swap=f"multi:#{form_id},#order-button-wrapper",
        )[
            form["plus"].as_widget(SubmitWidget("+ Lägg till"))
            if not current_count
            else [
                form["minus"].as_widget(SubmitWidget("-")),
                form["count"].as_widget(attrs={"style": "text-align: center;"}),
                form["plus"].as_widget(SubmitWidget("+")),
            ]
        ],
    ]


def upcoming_pickups(producer: Producer) -> h.Node:
    all_pickups = list(producer.get_upcoming_pickups())
    if not all_pickups:
        return [
            h.strong["Inga kommande utlämningar"],
            h.br,
            f"{producer.display_name} har inte anmält sig till några kommande utlämningar. Kika tillbaka senare!",
        ]

    pickups_by_date = defaultdict(list)
    for pickup in all_pickups:
        pickups_by_date[pickup.date].append(pickup)

    return [_upcoming_pickup(date=date, pickups=pickups) for date, pickups in pickups_by_date.items()]


def _upcoming_pickup(*, date: datetime.date, pickups: list[Pickup]) -> h.Node:
    # Format date in Swedish: "torsdag 7 augusti"
    formatted_date = formats.date_format(date, "l j F")

    return [
        h.h3[f"Utlämning {formatted_date}"],
        h.ul[
            (
                h.li[f"{pickup.start_time.strftime('%H:%M')}–{pickup.end_time.strftime('%H:%M')}: {pickup.place}"]
                for pickup in pickups
            )
        ],
    ]


def producer_header_full(producer: Producer) -> h.Element:
    return h.header(".producer-header.full")[
        h.img(src=producer.image.url),
        h.article[
            h.h1[producer.display_name],
            h.p[producer.description],
            upcoming_pickups(producer),
        ],
    ]


def producer_header_minimal(producer: Producer) -> h.Element:
    return h.header(".producer-header")[h.article[h.h1[producer.display_name]]]


def _order_button_tooltip() -> h.Element:
    return h.wa_tooltip(for_="order-button")["Minst 1 produkt måste väljas."]


def producer_index(
    request: HttpRequest, producer: Producer, product_cart_forms: ProductCartForms, cart: Cart
) -> h.Element:
    cart_total_count = cart.total_count()
    pluralized = pluralize(cart_total_count, "vara,varor")
    cart_is_empty = cart_total_count == 0

    return producer_base(
        request=request,
        producer=producer,
    )[
        producer_header_full(producer),
        h.main[
            h.section(".wa-grid", style="--min-column-size: 25ch;")[
                (product_card(request.path, product_cart_form) for product_cart_form in product_cart_forms.forms)
            ],
            [
                h.div("#order-button-wrapper")[
                    cart_is_empty and _order_button_tooltip(),
                    h.wa_button(
                        "#order-button.order-button",
                        # Apparently this is an easier way than to try and prevent clicks on a wa-button using the href attribute.  # noqa: E501
                        {"x-data": "", "@click": f'location.href = "{reverse("order", args=[producer.slug])}"'}
                        if not cart_is_empty
                        else {},
                        size="large",
                        variant="neutral",
                        disabled=cart_is_empty,
                    )[
                        h.wa_badge(appearance="filled outlined", variant="brand")[
                            f"{cart_total_count} {pluralized} / {format_price(cart.total_price())}",
                        ],
                        h.wa_divider(orientation="vertical"),
                        "Beställ!",
                        h.wa_icon(name="arrow-right"),
                    ],
                ]
            ],
        ],
    ]


def order(
    request: HttpRequest,
    producer: Producer,
    order_form: OrderForm,
    cart: Cart,
) -> h.Element:
    cart_is_empty = cart.total_count() == 0
    return producer_base(
        request=request,
        producer=producer,
        title="Beställning",
    )[
        producer_header_minimal(producer),
        h.main[
            h.section(".wa-grid", style="--min-column-size: 400px;")[
                h.wa_card[
                    h.h2["Varor"],
                    [
                        "Du har inte valt några produkter." if cart_is_empty else "Glömde du något?",
                        " ",
                        h.a(
                            href=reverse("producer-index", args=[producer.slug]),
                        )["Ändra produkter"],
                    ],
                    not cart_is_empty
                    and h.table(".wa-zebra-rows")[
                        h.thead[
                            h.tr[
                                h.th["Produkt"],
                                h.th["Antal"],
                                h.th["Styckpris"],
                                h.th["Summa"],
                            ]
                        ],
                        h.tbody[
                            (
                                h.tr[
                                    h.td[product.name],
                                    h.td[quantity],
                                    h.td[format_price(product.price)],
                                    h.td[format_price(product.price * quantity)],
                                ]
                                for product, quantity in cart.items.items()
                            )
                        ],
                        h.tfoot[
                            h.tr[
                                h.th(colspan="3")["Totalt"],
                                h.th[format_price(cart.total_price())],
                            ],
                        ],
                    ],
                ],
                h.wa_card(".order-form")[
                    h.form(method="post")[
                        csrf_input(request),
                        h.h2["Dina uppgifter"],
                        h.div(".wa-stack")[
                            _render_field(order_form["pickup"]),
                            _render_field(order_form["name"]),
                            _render_field(order_form["email"]),
                            _render_field(order_form["phone"]),
                            _render_field(order_form["note"]),
                            h.small[f"Betalning sker med Swish direkt till {producer.company_name}."],
                            cart_is_empty and _order_button_tooltip(),
                            h.button("#order-button.wa-brand", type="submit", disabled=cart_is_empty)["Beställ!"],
                        ],
                    ],
                ],
            ],
        ],
    ]


def _render_field(bound_field: BoundField) -> h.Element:
    return h.label[
        bound_field.label,
        bound_field.field.required and " *",
        bound_field,
        bound_field.errors,
    ]


def _order_summary_payment(order: Order) -> h.Element:
    producer = order.producer

    return h.wa_callout[
        h.wa_icon(slot="icon", name="circle-info"),
        "Betala med Swish: ",
        h.b[format_price(order.total_price())],
        " till ",
        h.b[producer.swish_number],
        ".",
    ]


def _order_summary_product_list(order: Order) -> h.Element:
    return h.table(".wa-zebra-rows")[
        h.thead[
            h.tr[
                h.th["Produkt"],
                h.th["Antal"],
                h.th["Pris"],
                h.th["Summa"],
            ]
        ],
        h.tbody[
            (
                h.tr[
                    h.td[order_product.name],
                    h.td[format_amount(order_product.amount)],
                    h.td[format_price(order_product.price)],
                    h.td[format_price(order_product.total_price())],
                ]
                for order_product in order.orderproduct_set.all()
            )
        ],
        h.tfoot[
            h.tr[
                h.th(colspan="3")["Totalt"],
                h.th[format_price(order.total_price())],
            ],
        ],
    ]


def _order_summary_details(order: Order) -> h.Element:
    return h.table[
        h.tr[h.th["Säljare"], h.td[order.producer.display_name]],
        h.tr[h.th["Beställningsnummer"], h.td[f"{order.order_number}"]],
        h.tr[h.th["Datum"], h.td[order.pickup.date.isoformat()]],
        h.tr[h.th["Utlämningsplats"], h.td[order.pickup.place]],
        h.tr[h.th["Tid för utlämning"], h.td[format_time_range(order.pickup.start_time, order.pickup.end_time)]],
    ]


def order_summary(*, request: HttpRequest, order: Order) -> h.Element:
    producer = order.producer
    return producer_base(
        request=request,
        title="Tack för din beställning!",
        producer=producer,
    )[
        producer_header_minimal(producer),
        h.main[
            h.section(".wa-grid", style="--min-column-size: 400px;")[
                h.wa_card[
                    h.h1["Tack för din beställning!"],
                    _order_summary_payment(order),
                    _order_summary_details(order),
                ],
                h.wa_card[_order_summary_product_list(order),],
            ]
        ],
    ]


def base_email(contents: h.Node) -> h.Element:
    return h.html[
        h.head[
            h.meta(charset="UTF-8"),
            h.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        ],
        h.body(
            style="""
            font-family: system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji",
                "Segoe UI Emoji", "Segoe UI Symbol";
            """
        )[
            h.table(width="100%", border="0", cellspacing="0", cellpadding="0")[
                h.tr[
                    h.td(align="center", style="padding: 20px;")[
                        h.table(
                            width="600",
                            border="0",
                            cellspacing="0",
                            cellpadding="0",
                            style="border-collapse: collapse; border: 1px solid #cccccc;",
                        )[
                            h.tr[
                                h.td(
                                    style="""
                                        background-color: #e3ffd5; padding: 40px; text-align: center;
                                            color: #5B8D20; font-size: 24px;
                                    """,
                                )["Handla REKO"]
                            ],
                            contents,
                            h.tr[
                                h.td(
                                    style="""
                                        background-color: #333333;
                                        padding: 40px;
                                        text-align: center;
                                        color: white;
                                        font-size: 14px;
                                    """,
                                )["Detta mejl skickades genom handlareko.se."]
                            ],
                        ]
                    ]
                ]
            ]
        ],
    ]


def _email_row(*contents: h.Node) -> h.Element:
    return h.tr[
        h.td(
            style="padding: 40px; text-align: left; font-size: 16px; line-height: 1.6;",
        )[contents]
    ]


def _email_button_section(*, text: str, url: str) -> h.Element:
    return _email_row(
        h.table(cellspacing="0", cellpadding="0", style="margin: auto;")[
            h.tr[
                h.td(
                    align="center",
                    style="background-color: #398713; padding: 10px 20px; border-radius: 5px;",
                )[
                    h.a(
                        href=url,
                        target="_blank",
                        style="color: #ffffff; text-decoration: none; font-weight: bold;",
                    )[text]
                ]
            ]
        ]
    )


def order_confirmation_email(*, order: Order, request: HttpRequest) -> h.Element:
    return base_email(
        contents=[
            _email_row(h.p[f"Tack för din beställning, {order.name}!"]),
            _email_row(_order_summary_payment(order)),
            _email_row(_order_summary_product_list(order)),
            _email_row(_order_summary_details(order)),
            _email_button_section(
                text="Visa beställning",
                url=order.order_summary_url(request),
            ),
        ]
    )
