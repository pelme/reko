from decimal import ROUND_UP, Decimal


def format_price(price: Decimal) -> str:
    kronor = int(price)
    ore = price % 1

    ore_str = str(int(ore * 100)).zfill(2) if ore else "-"

    return f"{kronor}:{ore_str}"


def format_amount(amount: Decimal) -> str:
    # display with decimals if not a whole number
    if amount % 1:
        return f"{amount:.2f}"
    return str(int(amount))


def quantize_decimal(number: Decimal) -> Decimal:
    return number.quantize(Decimal("0.00"), rounding=ROUND_UP)
