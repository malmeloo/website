from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import reverse, redirect

from apps.api.models import TempStateCode
from . import gphotos_api

ALLOWED_EMAILS = settings.CONFIG.get('gphotos.allowedEmails', [])


def login(request: HttpRequest):
    if not gphotos_api.can_operate():
        return HttpResponse('Error: clientId or clientSecret is missing, update config!', status=500)

    url = gphotos_api.get_callback_url(
        request.build_absolute_uri(reverse(callback)),
        TempStateCode.generate('gphotos').state_code
    )
    return redirect(url)


def callback(request: HttpRequest):
    if not gphotos_api.can_operate():
        return HttpResponse('Error: clientId or clientSecret is missing, update config!', status=500)

    state = request.GET.get('state')
    if state is None or not TempStateCode.verify('gphotos', state):
        # 400 bad request
        return HttpResponse('Error: missing or invalid state parameter', status=400)

    code = request.GET.get('code')
    if code is None:
        # 400 bad request
        return HttpResponse('Error: missing code parameter', status=400)

    # exchange code for token
    token, id_token = gphotos_api.resolve_access_token(code, request.build_absolute_uri().split('?')[0])
    if token is None:
        # 500 internal server error
        return HttpResponse('Error while retrieving authentication token', status=500)

    email = gphotos_api.get_email(id_token or '')
    if email not in ALLOWED_EMAILS:
        return HttpResponse(f'Error: account is not in the allowlist ({email})', status=403)

    token.save()

    return HttpResponse(f'Done! Logged in as {email}')
