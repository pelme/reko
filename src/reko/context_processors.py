from django.conf import settings

from django.http import HttpRequest


def site_name(request: HttpRequest) -> dict[str, str]:
    return {
        "SITE_NAME": settings.SITE_NAME,
    }
