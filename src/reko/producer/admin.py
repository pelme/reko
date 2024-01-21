from django.contrib import admin

from .models import Category, Producer


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin[Producer]):
    pass


admin.site.register(Category)
