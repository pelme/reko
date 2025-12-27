from __future__ import annotations

import importlib.resources
import typing as t
from collections import defaultdict
from decimal import Decimal

import htpy as h
import markdown
from django.middleware.csrf import get_token
from django.template.backends.utils import csrf_input
from django.template.defaultfilters import pluralize
from django.templatetags.static import static
from django.urls import reverse
from markupsafe import Markup

import reko
from reko.reko.utils.vat import vat_amount

from .formatters import (
    format_amount,
    format_date,
    format_percentage,
    format_price,
    format_swish_number,
    format_time_range,
)
from .forms import OrderForm, ProductCartForm, ProductCartForms, SubmitWidget
from .symbols import EN_DASH

if t.TYPE_CHECKING:
    import datetime

    from django.forms import BoundField
    from django.http import HttpRequest

    from .cart import Cart
    from .models import Order, Pickup, Producer


@h.with_children
def base(
    content: h.Node,
    *,
    request: HttpRequest,
    title: str,
    brand_color: str,
    body_class: str | None = None,
) -> h.Element:
    return h.html(lang="sv", class_=f"wa-theme-default wa-brand-{brand_color} wa-cloak")[
        h.head[
            h.meta(charset="utf-8"),
            h.meta(
                name="viewport", content="width=device-width, initial-scale=1.0, user-scalable=no, viewport-fit=cover"
            ),
            h.title[f"{title} {EN_DASH} Handla REKO"],
            h.style[
                # Avoid Flash of Undefined Custom Elements (FOUCE):
                # https://www.abeautifulsite.net/posts/flash-of-undefined-custom-elements/
                ":not(:defined) { visibility: hidden; }"
            ],
            h.link(rel="stylesheet", href=static("vendor/webawesome/styles/webawesome.css")),
            h.link(rel="stylesheet", href=static("vendor/webawesome/styles/themes/default.css")),
            h.script(type="module", src=static("vendor/webawesome/webawesome.loader.js")),
            h.link(rel="stylesheet", href=static("reko/reko.css")),
            h.link(rel="shortcut icon", href=static("reko/favicon.webp")),
            h.script(defer=True, src=static("vendor/alpinejs.min.js")),
            h.script(defer=True, src=static("vendor/htmx.min.js")),
            h.script(defer=True, src=static("vendor/multi-swap.js")),
        ],
        h.body(
            hx_headers=f'{{"X-CSRFToken": "{get_token(request)}"}}',
            hx_ext="multi-swap",
            class_=body_class,
        )[
            [
                content,
                h.footer[
                    h.hr,
                    h.section(".wa-cluster.wa-gap-xl")[
                        (
                            h.a(href=reverse("index"))["Start"],
                            h.a(href=reverse("about"))["Om handlareko.se"],
                        )
                    ],
                ],
            ]
        ],
    ]


def static_content(*, request: HttpRequest, title: str, markdown_file: str) -> h.Renderable:
    markdown_content = importlib.resources.read_text(reko, f"content/{markdown_file}")
    html_content = markdown.markdown(markdown_content)
    return base(
        title=title,
        request=request,
        brand_color="purple",
    )[h.main[h.article(".static-content")[Markup(html_content),]]]


def index_page(*, request: HttpRequest) -> h.Renderable:
    return base(title="Välkommen", request=request, brand_color="purple")[
        h.main[
            h.section(".hero")[
                h.header[
                    h.h1["Välkommen till handlareko.se!",],
                    h.p["Handla närproducerad mat direkt från lokala producenter.",],
                    h.wa_button(href="/demo", variant="brand", size="large", pill=True)[
                        "Testa demoproducenten",
                        h.wa_icon(slot="end", name="arrow-right"),
                    ],
                ],
            ],
            h.article(".static-content")[
                h.section[
                    h.h2["Om REKO"],
                    h.p[
                        "En REKO-ring är ett sätt att sälja närproducerad mat helt utan mellanhänder. "
                        "I din lokala REKO-ring handlar du råvaror och produkter direkt från producenten. Se ",
                        h.a(href="https://hushallningssallskapet.se/tjanster/landsbygd/reko/")[
                            "Hushållningssällskapets information om REKO-ringar för mer info."
                        ],
                    ],
                    h.p[
                        "handlareko.se är en webbtjänst för lokala REKO-ringar där producenter kan "
                        "lägga upp sina varor och konsumenter kan handla direkt av producenten.",
                    ],
                    h.h2["För dig som konsument"],
                    h.p["handlareko.se underlättar för dig som handlar på REKO-ringar."],
                    h.ul[
                        h.li["Du kan enkelt se de varor som en producent säljer. Priset räknas ut direkt."],
                        h.li["Du får ett mejl med en tydlig sammanställning över dina beställda varor."],
                        h.li["Inget konto krävs - allt du behöver ange är namn, mejladress och mobilnummer."],
                        h.li[
                            "Betalningen sker direkt mellan dig och producenten via Swish. "
                            "handlareko.se drivs ideellt och tar inte ut några extra avgifter."
                        ],
                        h.li["Bara du själv och producenten ser vad du har beställt."],
                        h.li["(Kommande) Upphämtningslistor där du kan bocka av de produkter du har hämtat ut."],
                    ],
                    h.p[
                        "Varje producent på handlareko.se får sin egen länk som de sedan delar via "
                        "Facebook eller direkt till dig som konsument."
                    ],
                    h.p[h.strong["Tipsa gärna dina favoritproducenter om att sälja sina varor här!"],],
                    h.h2["För dig som producent"],
                    h.p["handlareko.se underlättar och minskar den administrativa bördan för dig som producent:"],
                    h.ul[
                        h.li["Automatisk hantering av beställningar och uträkning av priser."],
                        h.li[
                            "Beställningar tas emot på ett strukturerat sätt utan att du måste "
                            "följa många Facebook-kommentarer."
                        ],
                        h.li[
                            "Du lägger enkelt själv upp dina produkter som är till försäljning. "
                            "Du kan när som helst dölja en vara om den är slutsåld."
                        ],
                        h.li["Du får en tydlig lista över beställningar och belopp."],
                        h.li[
                            "Du kan lägga upp dina varor en gång och anmäla dig till flera olika "
                            "ringar och utlämningar."
                        ],
                        h.li[
                            "Du får en unik länk till just din sida (t.ex. https://handlareko.se/honungsboden) "
                            "som du kan dela på Facebook eller direkt till dina kunder."
                        ],
                        h.li[
                            "Betalningen sker direkt mellan kunden och dig som producent via Swish. "
                            "handlareko.se drivs ideellt och tar inte ut några extra avgifter."
                        ],
                        h.li["(Kommande) Exportera underlag till bokföring/redovisning."],
                        h.li[
                            "(Kommande) Skicka ut automatiska påminnelser till kunder för att undvika "
                            "bortglömda upphämtningar."
                        ],
                    ],
                    h.p[
                        h.strong[
                            "Är du producent och vill sälja genom handlareko.se? Hör av dig till oss på ",
                            h.a(href="mailto:hej@handlareko.se")["hej@handlareko.se"],
                            " så hjälper vi dig igång!",
                        ],
                    ],
                    h.h2["För dig som är admin för en REKO-ring"],
                    h.ul[
                        h.li["Lägg upp kommande utlämningar med tid/plats."],
                        h.li[
                            "(Kommande) Ha en samlingssida för ringen med producenter som kommer till "
                            "en viss utlämning."
                        ],
                    ],
                    h.p[
                        h.strong[
                            "Vill du göra det möjligt för producenter i din ring att använda handlareko.se? "
                            "Hör av dig till oss på ",
                            h.a(href="mailto:hej@handlareko.se")["hej@handlareko.se"],
                            "!",
                        ],
                    ],
                    h.h2["Vill du veta mer?"],
                    h.p[
                        "Vi har samlat mer info om handlareko.se-projektet på ",
                        h.a(href=reverse("about"))["Om handlareko.se"],
                        ".",
                    ],
                ],
            ],
        ]
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
        title=(f"{title} {EN_DASH} " if title else "") + producer.display_name,
        brand_color=producer.color_palette,
        body_class="limit-width",
    )[content]


def product_card(url: str, form: ProductCartForm, has_upcoming_pickup: bool) -> h.Element:
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
                h.span[format_price(product.price_with_vat)],
            ],
            h.p(style="flex: 1")[product.description],
        ],
        has_upcoming_pickup
        and h.form(
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
    return [
        h.h3[f"Utlämning {format_date(date)}"],
        h.ul[(h.li[f"{format_time_range(pickup.start_time, pickup.end_time)}: {pickup.place}"] for pickup in pickups)],
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
    has_upcoming_pickup = producer.get_upcoming_pickups().exists()
    has_products = len(product_cart_forms.forms) > 0

    return producer_base(
        request=request,
        producer=producer,
    )[
        producer_header_full(producer),
        h.main[
            h.section(".wa-grid", style="--min-column-size: 25ch;")[
                (
                    product_card(request.path, product_cart_form, has_upcoming_pickup)
                    for product_cart_form in product_cart_forms.forms
                )
                if has_products
                else h.p(style="text-align: center")[f"{producer.display_name} har inga tillgängliga produkter."]
            ],
            [
                has_upcoming_pickup
                and has_products
                and h.div("#order-button-wrapper")[
                    cart_is_empty and _order_button_tooltip(),
                    h.wa_button(
                        ".order-button",
                        # Apparently this is an easier way than to try and prevent clicks on a wa-button using the href attribute. # noqa: E501
                        {"x-data": "", "@click": f'location.href = "{reverse("order", args=[producer.slug])}"'}
                        if not cart_is_empty
                        else {},
                        size="large",
                        variant="neutral",
                        disabled=cart_is_empty,
                    )[
                        h.wa_badge(appearance="filled outlined", variant="brand")[
                            f"{cart_total_count} {pluralized} / {format_price(cart.total_price_with_vat())}",
                        ],
                        h.wa_divider(orientation="vertical"),
                        "Beställ!",
                        h.wa_icon(name="arrow-right"),
                    ],
                ]
            ],
        ],
    ]


def _order_submit_button(*attrs: t.Mapping[str, h.Attribute], **kwargs: h.Attribute) -> h.Element:
    return h.wa_button(".wa-brand", *attrs, **kwargs)["Beställ!"]


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
                                    h.td[format_price(product.price_with_vat)],
                                    h.td[format_price(product.price_with_vat * quantity)],
                                ]
                                for product, quantity in cart.items.items()
                            )
                        ],
                        h.tfoot[
                            h.tr[
                                h.th(colspan="3")["Totalt"],
                                h.th[format_price(cart.total_price_with_vat())],
                            ],
                        ],
                    ],
                ],
                h.wa_card(".order-form")[
                    h.form({"x-data": r"{submitting: false}", "@submit.once": "submitting = true"}, method="post")[
                        csrf_input(request),
                        h.h2["Dina uppgifter"],
                        h.div(".wa-stack")[
                            _render_field(order_form["pickup"], {"class": "pickup-select"}),
                            _render_field(order_form["name"]),
                            _render_field(order_form["email"]),
                            _render_field(order_form["phone"]),
                            _render_field(order_form["note"]),
                            h.small[f"Betalning sker med Swish direkt till {producer.company_name}."],
                            cart_is_empty and _order_button_tooltip(),
                            h.template(x_if="!submitting")[_order_submit_button(type="submit", disabled=cart_is_empty)],
                            h.template(x_if="submitting")[_order_submit_button(type="button", loading=True)],
                        ],
                    ],
                ],
            ],
        ],
    ]


def _render_field(bound_field: BoundField, label_attrs: dict[str, h.Attribute] | None = None) -> h.Element:
    return h.label(label_attrs or {})[
        bound_field.label,
        bound_field.field.required and " *",
        bound_field,
        bound_field.errors,
    ]


def _order_summary_payment(order: Order) -> h.Element:
    producer = order.producer

    return h.wa_callout(".order-summary-payment")[
        h.wa_icon(slot="icon", name="circle-info"),
        "Betala med Swish: ",
        h.b[format_price(order.total_price_with_vat())],
        " till ",
        h.b[format_swish_number(producer.swish_number)],
        ".",
    ]


def _order_summary_product_list(order: Order) -> h.Element:
    amount_by_vat_factor: dict[Decimal, Decimal] = defaultdict(Decimal)
    for order_product in order.orderproduct_set.all():
        amount_by_vat_factor[order_product.vat_factor] += vat_amount(
            order_product.total_price_with_vat(), order_product.vat_factor
        )

    return h.table(".wa-zebra-rows.order-summary")[
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
                    h.td[format_price(order_product.price_with_vat)],
                    h.td[format_price(order_product.total_price_with_vat())],
                ]
                for order_product in order.orderproduct_set.all()
            )
        ],
        h.tfoot[
            h.tr[
                h.th(colspan="3")["Totalt"],
                h.th[format_price(order.total_price_with_vat())],
            ],
            (
                h.tr[
                    h.th(colspan="3")[f"Varav {format_percentage(vat_factor)} moms"],
                    h.th[format_price(amount)],
                ]
                for vat_factor, amount in sorted(amount_by_vat_factor.items())
            ),
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


CONFIRMATION_SENT_BY_EMAIL_TEXT: t.Final[str] = """
    En bekräftelse har skickats till dig via mejl.
    Du kan också besöka den här sidan igen för att se din beställning.
    """
MAKING_CHANGES_TO_AN_ORDER_TEXT: t.Final[str] = """
    Om du vill beställa mer gör du enklast en ny beställning.
    Kontakta säljaren om du skulle behöva göra andra ändringar.
    """


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
                    h.h2["Tack för din beställning!"],
                    h.p[CONFIRMATION_SENT_BY_EMAIL_TEXT, MAKING_CHANGES_TO_AN_ORDER_TEXT],
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
            _email_row(h.p[MAKING_CHANGES_TO_AN_ORDER_TEXT]),
            _email_row(_order_summary_payment(order)),
            _email_row(_order_summary_product_list(order)),
            _email_row(_order_summary_details(order)),
            _email_button_section(
                text="Visa beställning",
                url=order.order_summary_url(request),
            ),
        ]
    )
