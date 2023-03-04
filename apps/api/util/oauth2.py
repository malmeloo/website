import json
import sys
import traceback
from datetime import timedelta
from urllib.parse import urlencode

import httpx
from django.utils import timezone

from apps.api.models import OAuthToken

client = httpx.Client()


def request(method, url, auth_token=None, data=None, extra_headers=None):
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }
    headers.update(extra_headers or {})

    try:
        r = client.request(method, url, headers=headers, data=data)
    except httpx.RequestError as e:
        traceback.print_exception(e)
        return None

    try:
        r.raise_for_status()
        return r.json()
    except (httpx.HTTPStatusError, json.JSONDecodeError) as e:
        traceback.print_exception(e)
        print(f'- Response: {r.text}', file=sys.stderr)
        return None


class OAuth2Provider:
    def __init__(self, provider, auth_endpoint, token_endpoint, client_id, client_secret):
        self._provider = provider

        self._auth_endpoint = auth_endpoint
        self._token_endpoint = token_endpoint
        self._redirect_uri = None

        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def can_operate(self):
        return not (self.client_id is None or self.client_secret is None)

    def set_redirect_uri(self, uri):
        self._redirect_uri = uri

    def _consume_token(self, **data):
        token = OAuthToken(
            service=self._provider,
            access_token=data.pop('access_token'),
            refresh_token=data.pop('refresh_token', None),
            scope=data.pop('scope'),
            expires_at=timezone.now() + timedelta(seconds=data.pop('expires_in', 0))
        )
        return token, data

    def _refresh_token(self, token: OAuthToken, extra=None):
        payload = {
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token
        }
        payload.update(extra or {})

        data = request('POST', self._token_endpoint, data=payload)
        if data is None:
            return None

        new_token, _ = self._consume_token(**data)
        new_token.refresh_token = token.refresh_token  # refresh token should be persistent
        new_token.save()  # will overwrite `token` in db

        return new_token

    def create_auth_url(self, scopes: list[str], extra=None):
        data = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self._redirect_uri,
            'scope': ' '.join(scopes)
        }
        data.update(extra or {})

        return f'{self._auth_endpoint}?{urlencode(data)}'

    def resolve_code(self, code: str, auth_token=None, extra_headers=None):
        payload = {
            'grant_type': 'authorization_code',
            'redirect_uri': self._redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code
        }

        data = request('POST', self._token_endpoint, data=payload, auth_token=auth_token, extra_headers=extra_headers)
        if data is None:
            return None

        return self._consume_token(**data)

    def get_access_token(self, refresh_extra=None):
        try:
            token = OAuthToken.objects.get(service='spotify')
        except OAuthToken.DoesNotExist:
            return None

        if token.expires_at < timezone.now():  # refresh token
            token = self._refresh_token(token, refresh_extra)
        return token
