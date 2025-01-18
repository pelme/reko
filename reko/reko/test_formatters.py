from decimal import Decimal

import pytest

from .formatters import format_amount, format_price, quantize_decimal


@pytest.mark.parametrize(
    ["price", "formatted_price"],
    [
        (Decimal("1337"), "1337 kr"),
        (Decimal("13.37"), "13,37 kr"),
        (Decimal("13.3700"), "13,37 kr"),
        (Decimal("1337.00"), "1337 kr"),
    ],
)
def test_format_price(price: Decimal, formatted_price: str) -> None:
    assert format_price(Decimal(price)) == formatted_price


@pytest.mark.parametrize(
    ["amount", "formatted_amount"],
    [
        (Decimal("1337"), "1337"),
        (Decimal("13.37"), "13,37"),
        (Decimal("13.3700"), "13,37"),
        (Decimal("1337.00"), "1337"),
    ],
)
def test_format_amount(amount: Decimal, formatted_amount: str) -> None:
    assert format_amount(Decimal(amount)) == formatted_amount


def test_quantize_decimal_truncates_zeroes() -> None:
    assert quantize_decimal(Decimal("1.0000")) == Decimal("1.00")


def test_quantize_decimal_rounds_up() -> None:
    assert quantize_decimal(Decimal("12.3456")) == Decimal("12.35")
