from django import template

from typing import Any

register = template.Library()


@register.filter
def add_class(field: Any, class_name: str) -> Any:
    return field.as_widget(attrs={"class": " ".join((field.css_classes(), class_name))})
