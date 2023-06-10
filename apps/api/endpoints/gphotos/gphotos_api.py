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


def can_operate() -> bool:
    return provider.can_operate


##############################
# Getting tokens / Auth flow #
##############################
def get_callback_url(redirect_uri: str, state_code: str) -> str:
    provider.set_redirect_uri(redirect_uri)
    return provider.create_auth_url(SCOPES, extra={'state': state_code, 'access_type': 'offline'})


def resolve_code(code: str, redirect_uri: str) -> tuple[OAuthToken | None, str | None]:
    provider.set_redirect_uri(redirect_uri)
    data = provider.resolve_code(code)
    token = data[0] if data else None
    extra = data[1].get('id_token', None) if data else None
    return token, extra


def get_access_token() -> OAuthToken | None:
    return provider.get_access_token()


#########
# Utils #
#########
def get_email(id_token: str) -> str | None:
    try:
        part = b64decode(id_token.split('.')[1] + '===')
        data = json.loads(part)
    except (KeyError, json.JSONDecodeError):
        return None

    return data.get('email', None)


def _request(method: str, url: str, token: OAuthToken, inner_key: str, data: dict | None = None) -> list:
    """Makes an authenticated request. Automatically resolves pagination."""
    req_data = data or {}
    result = []

    def request_once(page_token: str | None = None):
        if page_token is not None:
            req_data['pageToken'] = page_token
        resp = request(method, url, auth_token=token.access_token, data=req_data)
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
