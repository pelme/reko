from decimal import Decimal

import pytest

from reko.reko.factories import OrderFactory, OrderProductFactory

from .models import OrderProduct


class Test_OrderProduct:
    @pytest.mark.parametrize(
        ["price_with_vat", "amount", "expected_total_price"],
        [
            (Decimal("1337"), Decimal(0), Decimal(0)),
            (Decimal("1337"), Decimal(2), Decimal("2674")),
            (Decimal("1337"), Decimal("3.4"), Decimal("4545.80")),
        ],
    )
    def test_total_price_with_vat(
        self, price_with_vat: Decimal, amount: Decimal, expected_total_price: Decimal
    ) -> None:
        assert OrderProduct(price_with_vat=price_with_vat, amount=amount).total_price_with_vat() == expected_total_price


class Test_Order:
    @pytest.mark.django_db
    def test_total_price_with_vat(self) -> None:
        order = OrderFactory.create()
        OrderProductFactory.create(
            order=order, price_with_vat=Decimal("2674"), amount=Decimal("0.5"), vat_factor=Decimal("0.06")
        )
        OrderProductFactory.create(
            order=order, price_with_vat=Decimal("26.90"), amount=Decimal(2), vat_factor=Decimal("0.12")
        )
        assert order.total_price_with_vat() == Decimal("1390.80")
