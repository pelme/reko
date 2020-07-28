from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from reko.sellers.models import Seller


def start(request: HttpRequest) -> HttpResponse:
    return render(request, "index.html", {"seller_list": Seller.objects.all()})
