import os

import dj_database_url

from ._base import *  # noqa

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS: list[str] = ["handlareko.se"]

if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config()}

MEDIA_URL = "/media/"
MEDIA_ROOT = "/reko/media"

STATIC_ROOT = "/reko/static"
