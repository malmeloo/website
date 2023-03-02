import json
import sys
from base64 import b64decode
from datetime import timedelta
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.utils import timezone

from apps.api.models import OAuthToken

CLIENT_ID = settings.CONFIG.get('gphotos.clientId')
CLIENT_SECRET = settings.CONFIG.get('gphotos.clientSecret')

AUTH_ENDPOINT = 'https://accounts.google.com/o/oauth2/v2/auth'
TOKEN_ENDPOINT = 'https://oauth2.googleapis.com/token'
SCOPES = 'openid email https://www.googleapis.com/auth/photoslibrary.readonly'

client = httpx.Client()


def can_operate():
    return not (CLIENT_ID is None or CLIENT_SECRET is None)


def _make_token(**data):
    return OAuthToken(
        service='gphotos',
        access_token=data.get('access_token'),
        refresh_token=data.get('refresh_token'),
        scope=data.get('scope'),
        expires_at=timezone.now() + timedelta(seconds=data.get('expires_in', 0))
    )


def _request(method, url, auth_token=None, data=None):
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        r = client.request(method, url, headers=headers, data=data)
        r.raise_for_status()
        return r.json()
    except (httpx.RequestError, httpx.HTTPStatusError, json.JSONDecodeError) as e:
        print(e, file=sys.stderr)
        return None


def get_callback_url(redirect_uri, state_code):
    qs = urlencode({
        'response_type': 'code',
        'access_type': 'offline',
        'client_id': CLIENT_ID,
        'scope': SCOPES,
        'redirect_uri': redirect_uri,
        'state': state_code
    })
    return AUTH_ENDPOINT + '?' + qs


def resolve_access_token(code, redirect_uri):
    data = _request('POST', TOKEN_ENDPOINT, data={
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': redirect_uri
    })
    if data is None:
        return None

    return _make_token(**data), data.get('id_token', None)


def get_email(id_token: str):
    try:
        part = b64decode(id_token.split('.')[1] + '===')
        data = json.loads(part)
    except (KeyError, json.JSONDecodeError):
        return None

    return data.get('email', None)
