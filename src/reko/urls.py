from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from .order.views import order, order_summary
from .start.views import index, index_producers

urlpatterns = [
    path("", index, name="index"),
    path("admin/", admin.site.urls),
    path("_producers", index_producers, name="index-producers-all"),
    path(
        "_producers/<int:category_id>",
        index_producers,
        name="index-producers-category",
    ),
    path("beställning/<str:signed_order_id>", order_summary, name="order-summary"),
    path("<path:producer_slug>", order, name="order"),
]


if getattr(settings, "SERVE_DEV_MEDIA", False):
    urlpatterns = [
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *urlpatterns,
    ]
