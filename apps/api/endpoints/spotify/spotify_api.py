import base64
import json
import sys
from datetime import timedelta
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.utils import timezone

from apps.api.models import OAuthToken

CLIENT_ID = settings.CONFIG.get('spotify.clientId')
CLIENT_SECRET = settings.CONFIG.get('spotify.clientSecret')

API_ENDPOINT = 'https://api.spotify.com/v1'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
AUTHORIZE_CALLBACK = 'https://accounts.spotify.com/authorize'
SCOPES = 'user-read-email user-top-read'

HEADERS = {
    'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
}

client = httpx.Client()


def can_operate():
    return not (CLIENT_ID is None or CLIENT_SECRET is None)


def _request(method, url, auth_token=None, data=None):
    headers = {
        'Authorization': f'Bearer {auth_token}'
    } if auth_token else HEADERS

    try:
        r = client.request(method, url, headers=headers, data=data)
        r.raise_for_status()
        return r.json()
    except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
        print(e, file=sys.stderr)
        return None


def _make_token(**data):
    token = OAuthToken(
        service='spotify',
        access_token=data.get('access_token'),
        refresh_token=data.get('refresh_token'),
        scope=data.get('scope'),
        expires_at=timezone.now() + timedelta(seconds=data.get('expires_in', 0))
    )
    token.save()

    return token


def _refresh_token(token: OAuthToken):
    data = _request('POST', TOKEN_URL, data={
        'grant_type': 'refresh_token',
        'refresh_token': token.refresh_token
    })
    if data is None:
        return None

    token = _make_token(**data)
    token.save()

    return token


def get_callback_url(redirect_uri, state_code):
    qs = urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPES,
        'redirect_uri': redirect_uri,
        'show_dialog': True,
        'state': state_code
    })
    return AUTHORIZE_CALLBACK + '?' + qs


def resolve_access_token(code, redirect_uri):
    data = _request('POST', TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri
    })
    if data is None:
        return None

    return _make_token(**data)


def get_access_token():
    try:
        token = OAuthToken.objects.get(service='spotify')
    except OAuthToken.DoesNotExist:
        return None

    if token.expires_at < timezone.now():  # refresh token
        token = _refresh_token(token)
    return token


def get_user_profile(token: OAuthToken):
    return _request('GET', API_ENDPOINT + '/me',
                    auth_token=token.access_token)


def get_top_songs(token: OAuthToken):
    return _request('GET', API_ENDPOINT + '/me/top/tracks?time_range=short_term',
                    auth_token=token.access_token)
