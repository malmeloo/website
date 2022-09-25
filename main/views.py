from django.http import HttpResponse

from django.shortcuts import render


def index(request):
    ip = request.headers.get('CF-Connecting-IP')
    if not ip:
        ip = request.headers.get('X-Forwarded-For')
    if not ip:
        ip = request.META.get('REMOTE_ADDR')

    country = request.headers.get('CF-IPCountry')

    return render(request, 'index.html', {
        'ip': ip,
        'country_code': country
    })
