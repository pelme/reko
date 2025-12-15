from datetime import time
from decimal import Decimal

import pytest

from .formatters import format_amount, format_percentage, format_price, format_time_range, quantize_decimal
from .symbols import NBSP


@pytest.mark.parametrize(
    ["price", "formatted_price"],
    [
        (Decimal("1337"), f"1{NBSP}337{NBSP}kr"),
        (Decimal("13.37"), f"13,37{NBSP}kr"),
        (Decimal("13.3700"), f"13,37{NBSP}kr"),
        (Decimal("1337.00"), f"1{NBSP}337{NBSP}kr"),
    ],
)
def test_format_price(price: Decimal, formatted_price: str) -> None:
    assert format_price(Decimal(price)) == formatted_price


@pytest.mark.parametrize(
    ["amount", "formatted_amount"],
    [
        (Decimal("1337"), f"1{NBSP}337"),
        (Decimal("13.37"), "13,37"),
        (Decimal("13.3700"), "13,37"),
        (Decimal("1337.00"), f"1{NBSP}337"),
    ],
)
def test_format_amount(amount: Decimal, formatted_amount: str) -> None:
    assert format_amount(Decimal(amount)) == formatted_amount


def test_quantize_decimal_truncates_zeroes() -> None:
    assert quantize_decimal(Decimal("1.0000")) == Decimal("1.00")


def test_quantize_decimal_rounds_up() -> None:
    assert quantize_decimal(Decimal("12.3456")) == Decimal("12.35")


def test_format_time_range() -> None:
    assert format_time_range(time(12, 34, 56), time(23, 45, 12)) == "12:34–23:45"


@pytest.mark.parametrize(
    ["percentage", "formatted_percentage"],
    [
        (Decimal("1337"), f"133{NBSP}700{NBSP}%"),
        (Decimal("13.37"), f"1{NBSP}337{NBSP}%"),
        (Decimal("13.3700"), f"1{NBSP}337{NBSP}%"),
        (Decimal("1337.00"), f"133{NBSP}700{NBSP}%"),
        (Decimal("0.01337"), f"1,34{NBSP}%"),
    ],
)
def test_format_percentage(percentage: Decimal, formatted_percentage: str) -> None:
    assert format_percentage(percentage) == formatted_percentage
