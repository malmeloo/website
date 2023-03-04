from base64 import b64encode

import httpx
from django.conf import settings

from apps.api.models import OAuthToken
from apps.api.util.oauth2 import OAuth2Provider, request

API_ENDPOINT = 'https://api.spotify.com/v1'
SCOPES = ['user-read-email', 'user-top-read']

client = httpx.Client()
provider = OAuth2Provider(
    'spotify',
    'https://accounts.spotify.com/authorize',
    'https://accounts.spotify.com/api/token',

    settings.CONFIG.get('spotify.clientId', ''),
    settings.CONFIG.get('spotify.clientSecret', '')
)

EXTRA_HEADERS = {
    'Authorization': 'Basic ' + b64encode(f'{provider.client_id}:{provider.client_secret}'.encode()).decode()
}


def can_operate():
    return provider.can_operate


def get_callback_url(redirect_uri, state_code):
    provider.set_redirect_uri(redirect_uri)
    return provider.create_auth_url(SCOPES, extra={'state': state_code, 'show_dialog': True})


def resolve_code(code, redirect_uri):
    provider.set_redirect_uri(redirect_uri)
    data = provider.resolve_code(code, extra_headers=EXTRA_HEADERS)
    return data[0] if data is not None else None


def get_access_token():
    return provider.get_access_token()


def get_user_profile(token: OAuthToken):
    return request('GET', API_ENDPOINT + '/me',
                   auth_token=token.access_token)


def get_top_songs(token: OAuthToken):
    return request('GET', API_ENDPOINT + '/me/top/tracks?time_range=short_term',
                   auth_token=token.access_token)
