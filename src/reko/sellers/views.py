from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Seller


def seller_detail(request, slug):
    seller = get_object_or_404(Seller, slug=slug)
    return render(request, "seller.html", {"seller": seller})
