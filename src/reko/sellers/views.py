from django.http import HttpRequest, HttpResponse


def sellers_list(request: HttpRequest) -> HttpResponse:
    return HttpResponse("sellers")
