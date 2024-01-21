from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def format_price(price: Decimal) -> str:
    kronor = int(price)
    ore = price % 1

    ore_str = str(ore * 100).zfill(2) if ore else "-"

    return f"{kronor}:{ore_str}"
