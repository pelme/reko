from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from .start.views import start

urlpatterns = [
    path("", start),
    path("admin/", admin.site.urls),
]


if getattr(settings, "SERVE_DEV_MEDIA", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
