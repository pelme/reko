from typing import List

from ._base import *  # noqa
from ._base import PROJECT_ROOT

SECRET_KEY = "used-for-local-debugging-only"  # cspell:disable-line

DEBUG = True

ALLOWED_HOSTS: List[str] = []

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(PROJECT_ROOT / "db.sqlite3"),
    }
}

MEDIA_URL = "/media/"
MEDIA_ROOT = PROJECT_ROOT / ".dev-media"

SERVE_DEV_MEDIA = True
