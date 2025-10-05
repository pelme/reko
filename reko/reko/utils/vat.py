from decimal import Decimal


def vat_amount(price: Decimal, factor: Decimal) -> Decimal:
    return price * factor
