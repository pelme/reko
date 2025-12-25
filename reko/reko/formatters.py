from datetime import time
from decimal import ROUND_UP, Decimal

from django.utils.formats import number_format

from .symbols import EN_DASH, NBSP


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


def format_percentage(number: Decimal) -> str:
    return f"{format_amount(number * 100)}{NBSP}%"


def format_swish_number(number: str) -> str:
    if len(number) != 10:
        raise ValueError(f"Invalid length ({len(number)}) for a Swish number")
    return NBSP.join([number[:3], number[3:6], number[6:8], number[8:10]])
