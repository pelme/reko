from decimal import ROUND_UP, Decimal

from django.utils.formats import number_format


def format_price(price: Decimal) -> str:
    return f"{format_amount(price)} kr"


def format_amount(amount: Decimal) -> str:
    # display with decimals if not a whole number
    if amount % 1:
        return number_format(quantize_decimal(amount))
    return number_format(int(amount))


def quantize_decimal(number: Decimal) -> Decimal:
    return number.quantize(Decimal("0.00"), rounding=ROUND_UP)
