from datetime import time
from decimal import ROUND_UP, Decimal
from typing import Final, Literal

from django.utils.formats import number_format

NBSP: Final[Literal["\xa0"]] = "\xa0"
EN_DASH: Final[Literal["–"]] = "\u2013"


def format_price(price: Decimal) -> str:
    return f"{format_amount(price)}{NBSP}kr"


def format_amount(amount: Decimal) -> str:
    # display with decimals if not a whole number
    if amount % 1:
        return number_format(quantize_decimal(amount), force_grouping=True)
    return number_format(int(amount), force_grouping=True)


def quantize_decimal(number: Decimal) -> Decimal:
    return number.quantize(Decimal("0.00"), rounding=ROUND_UP)


def format_time_range(start: time, end: time) -> str:
    return f"{start.isoformat(timespec='minutes')}{EN_DASH}{end.isoformat(timespec='minutes')}"
