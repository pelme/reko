from __future__ import annotations

import dataclasses
import datetime
import typing as t
from decimal import Decimal
from urllib.parse import parse_qs

from .models import Product

if t.TYPE_CHECKING:
    from django.http import HttpRequest, HttpResponse

    from .models import Producer


def _get_cookie_name(producer: Producer) -> str:
    return f"cart-{producer.slug}"


@dataclasses.dataclass(frozen=True)
class Cart:
    producer: Producer
    items: dict[Product, int]

    @classmethod
    def from_cookie(cls, producer: Producer, request: HttpRequest) -> Cart:
        return cls.from_qs(
            producer,
            request.COOKIES.get(
                _get_cookie_name(producer),
                "",
            ),
        )

    @classmethod
    def empty(cls, producer: Producer) -> Cart:
        return cls(producer=producer, items={})

    def to_qs(self) -> str:
        return "&".join(f"{product.id}={count}" for product, count in self.items.items())

    def set_cookie(self, response: HttpResponse) -> None:
        cookie_name = _get_cookie_name(self.producer)

        if not self.items:
            response.delete_cookie(cookie_name)
            return

        response.set_cookie(
            cookie_name,
            self.to_qs(),
            max_age=datetime.timedelta(days=7),
            httponly=True,
            samesite="Lax",
        )

    @classmethod
    def from_qs(cls, producer: Producer, querystring: str) -> Cart:
        raw_query_dict = parse_qs(querystring)

        product_id_counts: dict[int, int] = {
            int(product_id): int(count[0])
            for product_id, count in raw_query_dict.items()
            if product_id.isdigit() and count[0].isdigit()
        }

        products_by_id: dict[int, Product] = {
            product.id: product
            for product in Product.objects.filter(producer=producer, id__in=product_id_counts.keys())
        }

        return cls(
            producer=producer,
            items={products_by_id[product_id]: count for product_id, count in product_id_counts.items()},
        )

    def total_count(self) -> int:
        return sum(count for count in self.items.values())

    def total_price(self) -> Decimal:
        return sum((product.price * count for product, count in self.items.items()), Decimal(0))

    def with_new_count(self, product: Product, new_count: int) -> Cart:
        return dataclasses.replace(self, items={**self.items, product: new_count})

    def get_count(self, product: Product) -> int:
        return self.items.get(product, 0)
