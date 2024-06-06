from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .reko import admin, views

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", admin.site.urls),
    path("<slug:producer_slug>", views.producer_index, name="producer-index"),
    path("<slug:producer_slug>/update/<int:product_id>", views.product_cart_update, name="product-card-update"),
    path("<slug:producer_slug>/bestall", views.order, name="order"),
]


if getattr(settings, "SERVE_DEV_MEDIA", False):
    urlpatterns = [
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
        *urlpatterns,
    ]
