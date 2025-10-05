from decimal import Decimal

import pytest

from .vat import vat_amount


@pytest.mark.parametrize(
    ["price_with_vat", "factor", "expected_vat_amount"],
    [
        (Decimal("1337"), Decimal(0), Decimal(0)),
        (Decimal("1337"), Decimal("0.06"), Decimal("80.22")),
        (Decimal("1337"), Decimal("0.12"), Decimal("160.44")),
        (Decimal("1337"), Decimal("0.25"), Decimal("334.25")),
    ],
)
def test_vat_amount(price_with_vat: Decimal, factor: Decimal, expected_vat_amount: Decimal) -> None:
    assert vat_amount(price_with_vat, factor) == expected_vat_amount
