import os

import dj_database_url
import sentry_sdk

from ._base import *  # noqa

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS: list[str] = ["handlareko.se"]

if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config()}

MEDIA_URL = "/media/"
MEDIA_ROOT = "/reko/media"

STATIC_ROOT = "/reko/static"

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.glesys.se"
EMAIL_PORT = 587
EMAIL_HOST_USER = "hej@handlareko.se"
EMAIL_HOST_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TIMEOUT = 3
EMAIL_USE_TLS = True

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

if "SENTRY_DSN" in os.environ:
    sentry_sdk.init(
        dsn=os.environ["SENTRY_DSN"],
        traces_sample_rate=1.0,
    )
