from django.contrib import admin

from .models import Category, Producer


class ProducerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Category)
admin.site.register(Producer, ProducerAdmin)
