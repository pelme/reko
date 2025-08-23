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


def base(
    *,
    request: HttpRequest,
    title: str,
    content: h.Node,
    header_content: h.Node = None,
    cart: h.Node = None,
    brand_color: str = "gray",
) -> h.Element:
    return h.html(
        f".wa-theme-default.wa-palette-rudimentary.wa-brand-{brand_color}.wa-neutral-gray.wa-success-green.wa-warning-yellow.wa-danger-red",
        lang="sv",
    )[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(
                name="viewport",
                content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover",
            ),
            h.title[f"{title} - Handla REKO"],
            h.style[
                # Avoid Flash of Undefined Custom Elements (FOUCE):
                # https://www.abeautifulsite.net/posts/flash-of-undefined-custom-elements/
                ":not(:defined) { visibility: hidden; }"
            ],
            h.link(
                rel="stylesheet", href="https://early.webawesome.com/webawesome@3.0.0-beta.3/dist/styles/webawesome.css"
            ),
            h.link(
                rel="stylesheet",
                href="https://early.webawesome.com/webawesome@3.0.0-beta.3/dist/styles/themes/default.css",
            ),
            h.link(
                rel="stylesheet",
                href="https://early.webawesome.com/webawesome@3.0.0-beta.3/dist/styles/color/palettes/rudimentary.css",
            ),
            h.script(
                type="module", src="https://early.webawesome.com/webawesome@3.0.0-beta.3/dist/webawesome.loader.js"
            ),
            # h.script(type="module", data_fa_kit_code="")[
            #     Markup(""" import { setDefaultIconFamily } from 'https://early.webawesome.com/webawesome@3.0.0-beta.3/dist/webawesome.js';
            # setDefaultIconFamily('classic');""")
            # ],
            h.link(rel="stylesheet", href=static("reko/reko.css")),
            h.link(rel="shortcut icon", href=static("reko/favicon.webp")),
            h.script(defer=True, src=static("vendor/alpinejs.min.js")),
            h.script(defer=True, src=static("vendor/htmx.min.js")),
        ],
        h.body(hx_headers='{"X-CSRFToken": "%s"}' % get_token(request))[  # noqa: UP031
            h.header[
                h.div(".container")[
                    header_content,
                    cart,
                ],
            ],
            h.main(".container.wa-stack")[content],
            h.footer(".container.wa-stack")[
                h.wa_divider,
                h.div(".wa-cluster.wa-gap-xl")[
                    h.a(href="/")["Om handlareko.se"],
                    h.a(href="#")["Bli en försäljare"],
                    h.a(href="#")["Kontakt"],
                ],
            ],
        ],
    ]


def producer_base(
    *,
    request: HttpRequest,
    producer: Producer,
    title: str = "",
    content: h.Node,
    cart: Cart | None = None,
) -> h.Element:
    if cart:
        cart_total_count = cart.total_count()
        pluralized = pluralize(cart_total_count, "vara,varor")
        cart_element = h.a(".cart", href=reverse("order", args=[producer.slug]))[
            basket_icon(),
            f"{cart_total_count} {pluralized}, {format_price(cart.total_price())}",
        ]
    else:
        cart_element = None
    return base(
        request=request,
        title=(f"{title} - " if title else "") + producer.display_name,
        header_content=[h.h1[producer.display_name]],
        content=content,
        cart=cart_element,
        brand_color=producer.color_palette,
    )


def product_card(url: str, form: ProductCartForm) -> h.Element:
    product = form.product

    current_count = form.initial.get("count", 0)

    return h.wa_card(".product.wa-card")[
        h.img(
            slot="media",
            loading="lazy",
            src=str(product.card_thumbnail.url),
            alt=product.name,
            height="150",
        ),
        h.div(".wa-flank.wa-flank:end.wa-align-items-start.wa-heading-m")[
            h.h4[product.name],
            h.span[format_price(product.price)],
        ],
        h.p(".description")[product.description],
        h.footer[
            h.form(
                role="group",
                hx_post=url,
                hx_trigger="submit,change",
                hx_target="body",
            )[
                (form["plus"].as_widget(SubmitWidget("+ Lägg till")),)
                if not current_count
                else [
                    form["minus"].as_widget(SubmitWidget("-")),
                    h.span(".current-count")[str(current_count)],
                    form["plus"].as_widget(SubmitWidget("+")),
                ]
            ],
        ],
    ]


def upcoming_pickups(producer: Producer) -> h.Node:
    all_pickups = list(producer.get_upcoming_pickups())
    if not all_pickups:
        return h.wa_callout(variant="danger")[
            h.wa_icon(slot="icon", name="circle-exclamation", variant="regular"),
            h.strong["Inga kommande utlämningar"],
            h.br,
            f"{producer.display_name} har inte anmält sig till några kommande utlämningar. Kika tillbaka senare!",
        ]

    pickups_by_date = defaultdict(list)
    for pickup in all_pickups:
        pickups_by_date[pickup.date].append(pickup)

    return [_upcoming_pickup(date=date, pickups=pickups) for date, pickups in pickups_by_date.items()]


def _upcoming_pickup(*, date: datetime.date, pickups: list[Pickup]) -> h.Element:
    # Format date in Swedish: "torsdag 7 augusti"
    formatted_date = formats.date_format(date, "l j F")

    return h.wa_callout(variant="brand")[
        h.wa_icon(slot="icon", name="circle-info", variant="regular"),
        h.strong[f"Utlämning {formatted_date}"],
        h.br,
        h.ul[
            (
                h.li[f"{pickup.start_time.strftime('%H:%M')}–{pickup.end_time.strftime('%H:%M')}: {pickup.place}"]
                for pickup in pickups
            )
        ],
    ]


def producer_index(
    request: HttpRequest, producer: Producer, product_cart_forms: ProductCartForms, cart: Cart
) -> h.Element:
    return producer_base(
        request=request,
        producer=producer,
        cart=cart,
        content=(
            h.section(".introduction")[h.p[producer.description],],
            h.section[upcoming_pickups(producer)],
            h.section(".products-grid")[
                (product_card(request.path, product_cart_form) for product_cart_form in product_cart_forms.forms)
            ],
            h.section(style="display: flex; justify-content: flex-end;")[
                h.a(
                    href=reverse("order", args=[producer.slug]),
                )["Fortsätt till beställning", arrow_right_icon(style="margin-left: .4rem;")]
            ],
        ),
    )


def order(
    request: HttpRequest,
    producer: Producer,
    order_form: OrderForm,
    cart: Cart,
) -> h.Element:
    return producer_base(
        request=request,
        producer=producer,
        title="Beställning",
        content=(
            h.section(".introduction")[h.h2["Beställ dina varor"],],
            h.a(
                style="align-self: flex-start;",
                href=reverse("producer-index", args=[producer.slug]),
            )[arrow_left_icon(style="margin-right: .4rem;"), "Tillbaka till produkter"],
            h.div(".order-layout")[
                h.form(".order-form", method="post")[
                    csrf_input(request),
                    h.div[
                        h.h2["Dina uppgifter"],
                        h.ul[
                            h.div(".form")[
                                _render_field(order_form["name"]),
                                _render_field(order_form["email"]),
                                _render_field(order_form["phone"]),
                                _render_field(order_form["pickup"]),
                                _render_field(order_form["note"]),
                                h.small[f"Betalning sker med Swish direkt till {producer.company_name}."],
                                h.button(".wa-brand", type="submit", class_="submit")["Beställ!"],
                            ],
                        ],
                    ],
                ],
                h.div(".order-summary")[
                    h.h2["Varor"],
                    h.table[
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
            ],
        ),
    )


def _render_field(form_field: BoundField) -> h.Element:
    return h.label[
        form_field.label,
        form_field,
        form_field.errors,
    ]


def _order_summary_payment(order: Order) -> h.Element:
    producer = order.producer
    return h.article[
        "Betala med Swish: ",
        h.b[format_price(order.total_price())],
        " till ",
        h.b[producer.swish_number],
        ".",
    ]


def _order_summary_table(order: Order) -> h.Element:
    return h.table(".striped")[
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
                h.td(colspan="3")["Totalt"],
                h.td[format_price(order.total_price())],
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
        content=h.section[
            h.h1["Tack för din beställning!"],
            _order_summary_payment(order),
            _order_summary_table(order),
            _order_summary_details(order),
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
            d="M5.757 1.071a.5.5 0 0 1 .172.686L3.383 6h9.234L10.07 1.757a.5.5 0 1 1 .858-.514L13.783 6H15a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1v4.5a2.5 2.5 0 0 1-2.5 2.5h-9A2.5 2.5 0 0 1 1 13.5V9a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h1.217L5.07 1.243a.5.5 0 0 1 .686-.172zM2 9v4.5A1.5 1.5 0 0 0 3.5 15h9a1.5 1.5 0 0 0 1.5-1.5V9zM1 7v1h14V7zm3 3a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3A.5.5 0 0 1 4 10m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3A.5.5 0 0 1 6 10m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3A.5.5 0 0 1 8 10m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3a.5.5 0 0 1 .5-.5m2 0a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-1 0v-3a.5.5 0 0 1 .5-.5"  # noqa: E501
        )
    ]


def arrow_left_icon(style: str) -> h.Element:
    # https://icons.getbootstrap.com/icons/arrow-left/
    return h.svg(
        ".bi.bi-arrow-left",
        style=style,
        xmlns="http://www.w3.org/2000/svg",
        width="16",
        height="16",
        fill="currentColor",
        viewBox="0 0 16 16",
    )[
        h.path(
            fill_rule="evenodd",
            d="M15 8a.5.5 0 0 0-.5-.5H2.707l3.147-3.146a.5.5 0 1 0-.708-.708l-4 4a.5.5 0 0 0 0 .708l4 4a.5.5 0 0 0 .708-.708L2.707 8.5H14.5A.5.5 0 0 0 15 8",  # noqa: E501
        )
    ]


def arrow_right_icon(style: str) -> h.Element:
    # https://icons.getbootstrap.com/icons/arrow-right/
    return h.svg(
        ".bi.bi-arrow-right",
        style=style,
        xmlns="http://www.w3.org/2000/svg",
        width="16",
        height="16",
        fill="currentColor",
        viewBox="0 0 16 16",
    )[
        h.path(
            fill_rule="evenodd",
            d="M1 8a.5.5 0 0 1 .5-.5h11.793l-3.147-3.146a.5.5 0 0 1 .708-.708l4 4a.5.5 0 0 1 0 .708l-4 4a.5.5 0 0 1-.708-.708L13.293 8.5H1.5A.5.5 0 0 1 1 8",  # noqa: E501
        )
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
            _email_row(_order_summary_table(order)),
            _email_row(_order_summary_details(order)),
            _email_button_section(
                text="Visa beställning",
                url=order.order_summary_url(request),
            ),
        ]
    )
