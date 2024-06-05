import dj_database_url

from ._base import *  # noqa
from ._base import PROJECT_ROOT

SECRET_KEY = "used-for-local-debugging-only"  # cspell:disable-line

DEBUG = True

ALLOWED_HOSTS: list[str] = ["*"]

DATABASES = {"default": dj_database_url.config(default="postgres:///reko")}

MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / ".dev-media"

SERVE_DEV_MEDIA = True
