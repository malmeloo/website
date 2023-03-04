import json
from base64 import b64decode

from django.conf import settings

from apps.api.models import OAuthToken
from apps.api.util.oauth2 import OAuth2Provider, request

API_ENDPOINT = 'https://photoslibrary.googleapis.com/v1'
SCOPES = ['openid', 'email', 'https://www.googleapis.com/auth/photoslibrary.readonly']

provider = OAuth2Provider(
    'gphotos',
    'https://accounts.google.com/o/oauth2/v2/auth',
    'https://oauth2.googleapis.com/token',

    settings.CONFIG.get('gphotos.clientId'),
    settings.CONFIG.get('gphotos.clientSecret')
)


def can_operate():
    return provider.can_operate


##############################
# Getting tokens / Auth flow #
##############################
def get_callback_url(redirect_uri, state_code):
    provider.set_redirect_uri(redirect_uri)
    return provider.create_auth_url(SCOPES, extra={'state': state_code, 'access_type': 'offline'})


def resolve_code(code, redirect_uri):
    provider.set_redirect_uri(redirect_uri)
    token, extra = provider.resolve_code(code)
    return token, extra.get('id_token', None)


def get_access_token():
    return provider.get_access_token()


#########
# Utils #
#########
def get_email(id_token: str):
    try:
        part = b64decode(id_token.split('.')[1] + '===')
        data = json.loads(part)
    except (KeyError, json.JSONDecodeError):
        return None

    return data.get('email', None)


def _request(method: str, url: str, token: OAuthToken, inner_key: str, data: dict = None):
    """Makes an authenticated request. Automatically resolves pagination."""
    data = data or {}
    result = []

    def request_once(page_token=None):
        if page_token is not None:
            data['pageToken'] = page_token
        resp = request(method, url, auth_token=token.access_token, data=data)
        if resp is None:
            return

        page_token, resp = resp.pop('nextPageToken', None), resp.get(inner_key)
        result.extend(resp)
        return page_token

    next_page_token = request_once()
    while next_page_token:
        next_page_token = request_once(next_page_token)

    return result


###############
# API Methods #
###############
def get_albums(token: OAuthToken):
    return _request('GET', API_ENDPOINT + '/albums',
                    token=token, inner_key='albums')


def get_image(token: OAuthToken, album_id: str):
    return _request('POST', API_ENDPOINT + '/mediaItems:search', token=token,
                    inner_key='mediaItems', data={'albumId': album_id})
