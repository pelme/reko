from django.contrib import admin
from django.urls import path

from .start.views import start

urlpatterns = [
    path("", start),
    path("admin/", admin.site.urls),
]
