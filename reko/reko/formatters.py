from decimal import Decimal


def format_price(price: Decimal) -> str:
    kronor = int(price)
    ore = price % 1

    ore_str = str(ore * 100).zfill(2) if ore else "-"

    return f"{kronor}:{ore_str}"


def format_amount(amount: Decimal) -> str:
    # display with decimals if not a whole number
    if amount % 1:
        return f"{amount:.2f}"
    return str(int(amount))
