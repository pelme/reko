from django.core.validators import RegexValidator


def SwishNumberValidator(message: str | None = None) -> RegexValidator:
    return RegexValidator(r"^(123|07[0-9])[0-9]{7}$", message=message)
