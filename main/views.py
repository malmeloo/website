from django.http import HttpResponse

from django.shortcuts import render


def index(request):
    print(request.headers)
    ip = request.META.get('X-Forwarded-For')
    if not ip:
        ip = request.META.get('REMOTE_ADDR')

    return render(request, 'index.html', {
        'ip': ip,
        'headers': '\n'.join(f'{name}: {value}' for name, value in request.headers.items())
    })
