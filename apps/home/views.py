from django.http import HttpRequest, HttpResponse


def root(request: HttpRequest) -> HttpResponse:
    return HttpResponse('<h1>Welcome</h1>')
