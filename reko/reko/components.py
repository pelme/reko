import htpy as h
from django.forms import BoundField
from django.http import HttpRequest
from django.middleware.csrf import get_token
from django.template.backends.utils import csrf_input
from django.templatetags.static import static
from django.urls import reverse

from .cart import Cart
from .formatters import format_amount, format_price, format_time_range
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
            h.title[f"{title} - Handla REKO"],
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
        h.body(hx_headers='{"X-CSRFToken": "%s"}' % get_token(request))[  # noqa: UP031
            h.header[
                h.div(".container")[
                    h.a(href=logo_url)[h.img(".logo", src=static("reko/logo.webp"), alt="Handla REKO logo")],
                    cart,
                ],
            ],
            h.main(".container")[content],
            h.footer[
                h.ul[
                    h.a(href="/")[h.li["Om handlareko.se"]],
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
        title=(f"{title} - " if title else "") + producer.display_name,
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
                h.figure(style=("border-radius: var(--pico-border-radius);overflow: hidden;"))[
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
                h.h1[producer.display_name],
                (
                    [
                        h.h2["Kommande utlämningar"],
                        h.ul[
                            (
                                h.li[
                                    f"{location.date}: "
                                    + f"{location.place} "
                                    + format_time_range(location.start_time, location.end_time)
                                ]
                                for location in upcoming_locations
                            )
                        ],
                    ]
                    if upcoming_locations
                    else h.p["Inga utlämningar planerade just nu."]
                ),
                h.p[producer.description],
            ],
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
    product_cart_forms: ProductCartForms,
) -> h.Element:
    return producer_base(
        request=request,
        producer=producer,
        title="Beställning",
        content=(
            h.section(".introduction")[
                h.h1[producer.display_name],
                h.h2["Beställ dina varor"],
            ],
            h.a(
                style="align-self: flex-start;",
                href=reverse("producer-index", args=[producer.slug]),
            )[arrow_left_icon(style="margin-right: .4rem;"), "Tillbaka till produkter"],
            h.form(method="post")[
                csrf_input(request),
                h.table(
                    "#order-summary.striped",
                    hx_post=reverse("order", args=[producer.slug]),
                    hx_select="#order-summary",
                    hx_target="#order-summary",
                    hx_swap="innerHTML",
                    hx_trigger="change",
                )[
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
                                h.td[form.product.name],
                                h.td[form["count"]],
                                h.td[format_price(form.product.price)],
                                h.td[format_price(form.product.price * cart.items[form.product])],
                            ]
                            for form in product_cart_forms.forms
                        )
                    ],
                    h.tfoot[
                        h.tr[
                            h.td(colspan="3")["Totalt"],
                            h.td[format_price(cart.total_price())],
                        ],
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
                            h.small[f"Betalning sker med Swish direkt till {producer.company_name}."],
                            product_cart_forms.errors,
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
        h.tr[h.th["Datum"], h.td[order.location.date.isoformat()]],
        h.tr[h.th["Utlämningsplats"], h.td[order.location.place]],
        h.tr[h.th["Tid för utlämning"], h.td[format_time_range(order.location.start_time, order.location.end_time)]],
    ]


def order_summary(*, request: HttpRequest, order: Order) -> h.Element:
    producer = order.producer
    return producer_base(
        request=request,
        title="Tack för din beställning!",
        producer=producer,
        content=h.section(".introduction")[
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
