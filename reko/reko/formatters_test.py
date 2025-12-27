from datetime import date, time
from decimal import Decimal

import pytest
import time_machine

from .formatters import (
    format_amount,
    format_date,
    format_percentage,
    format_price,
    format_swish_number,
    format_time_range,
    quantize_decimal,
)
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


@pytest.mark.parametrize(
    ["swish_number", "formatted_swish_number"],
    [
        ("1234567890", f"123{NBSP}456{NBSP}78{NBSP}90"),
        ("0706083841", f"070{NBSP}608{NBSP}38{NBSP}41"),
    ],
)
def test_format_swish_number(swish_number: str, formatted_swish_number: str) -> None:
    assert format_swish_number(swish_number) == formatted_swish_number


@pytest.mark.parametrize(
    "value",
    [
        "123",
        "01234567890",
    ],
)
def test_format_invalid_swish_number(value: str) -> None:
    with pytest.raises(ValueError, match=r"Invalid length \([0-9]+\) for a Swish number"):
        format_swish_number(value)


@pytest.mark.parametrize(
    ("value", "formatted_date"),
    [
        (date(2024, 8, 7), "onsdag 7 augusti 2024"),
        (date(2025, 8, 7), "torsdag 7 augusti"),
        (date(2026, 8, 7), "fredag 7 augusti 2026"),
    ],
)
@time_machine.travel(date(2025, 7, 8))
def test_format_date(value: date, formatted_date: str) -> None:
    assert format_date(value) == formatted_date
