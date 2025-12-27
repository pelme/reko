from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.urls import path

from .reko import admin, views

urlpatterns = [
    path("", views.index, name="index"),
    path("om-oss", views.about, name="about"),
    # This would unfortunately match the producer-index pattern...
    path("admin", lambda r: redirect("admin/", permanent=True)),
    path("admin/", admin.site.urls),
    path("demo", lambda r: redirect("producer-index", "demo-ostergarden", permanent=True)),
    path("<slug:producer_slug>", views.producer_index, name="producer-index"),
    path("<slug:producer_slug>/bestall", views.order, name="order"),
    path("<slug:producer_slug>/bestallning/<str:order_secret>", views.order_summary, name="order-summary"),
]


if getattr(settings, "SERVE_DEV_MEDIA", False):
    urlpatterns = [
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *urlpatterns,
    ]
