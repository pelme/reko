from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from reko.occasion.models import Occasion

from reko.producer.models import Category, Producer


def index(request: HttpRequest) -> HttpResponse:

    return render(
        request,
        "index.html",
        {
            "occasion": Occasion.objects.get_current(),
            "producers": Producer.objects.order_by("name"),
            "categories": Category.objects.order_by("name"),
        },
    )


def index_producers(request: HttpRequest, category_id: int = None) -> HttpResponse:
    all_producers = Producer.objects.order_by("name")

    if category_id:
        active_category = get_object_or_404(Category, id=category_id)
        producers = all_producers.filter(categories=active_category)
    else:
        active_category = None
        producers = all_producers

    return render(
        request,
        "partials/index_producers.html",
        {
            "active_category": active_category,
            "categories": Category.objects.order_by("name"),
            "producers": producers,
        },
    )
