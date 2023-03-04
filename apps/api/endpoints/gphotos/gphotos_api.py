import json
from base64 import b64decode

import httpx
from django.conf import settings

from apps.api.util.oauth2 import OAuth2Provider

SCOPES = ['openid', 'email', 'https://www.googleapis.com/auth/photoslibrary.readonly']

client = httpx.Client()
provider = OAuth2Provider(
    'gphotos',
    'https://accounts.google.com/o/oauth2/v2/auth',
    'https://oauth2.googleapis.com/token',

    settings.CONFIG.get('gphotos.clientId'),
    settings.CONFIG.get('gphotos.clientSecret')
)


def can_operate():
    return provider.can_operate


def get_callback_url(redirect_uri, state_code):
    provider.set_redirect_uri(redirect_uri)
    return provider.create_auth_url(SCOPES, extra={'state': state_code, 'access_type': 'offline'})


def resolve_code(code, redirect_uri):
    provider.set_redirect_uri(redirect_uri)
    token, extra = provider.resolve_code(code)
    return token, extra.get('id_token', None)


def get_email(id_token: str):
    try:
        part = b64decode(id_token.split('.')[1] + '===')
        data = json.loads(part)
    except (KeyError, json.JSONDecodeError):
        return None

    return data.get('email', None)
