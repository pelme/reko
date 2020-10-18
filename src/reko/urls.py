from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from .sellers.views import seller_detail
from .start.views import start

urlpatterns = [
    path("", start),
    path("admin/", admin.site.urls),
    path("<path:slug>/", seller_detail),
]


if getattr(settings, "SERVE_DEV_MEDIA", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
