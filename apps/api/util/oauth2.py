import json
import sys
import traceback
from datetime import timedelta
from typing import Any
from urllib.parse import urlencode

import httpx
from django.utils import timezone

from apps.api.models import OAuthToken

client = httpx.Client()


def request(method: str, url: str,
            auth_token: str | None = None,
            data: dict[str, Any] | None = None,
            extra_headers: dict[str, str] | None = None) -> Any:
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
    def __init__(self, provider: str,
                 auth_endpoint: str,
                 token_endpoint: str,
                 client_id: str,
                 client_secret: str):
        self._provider = provider

        self._auth_endpoint = auth_endpoint
        self._token_endpoint = token_endpoint
        self._redirect_uri: str | None = None

        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def can_operate(self) -> bool:
        return not (self.client_id is None or self.client_secret is None)

    def set_redirect_uri(self, uri: str) -> None:
        self._redirect_uri = uri

    def _consume_token(self, **data: Any) -> tuple[OAuthToken, dict[str, Any]]:
        token = OAuthToken(
            service=self._provider,
            access_token=data.pop('access_token'),
            refresh_token=data.pop('refresh_token', None),
            scope=data.pop('scope'),
            expires_at=timezone.now() + timedelta(seconds=data.pop('expires_in', 0))
        )
        return token, data

    def _refresh_token(self, token: OAuthToken, extra_headers: dict[str, str] | None = None) -> OAuthToken | None:
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': token.refresh_token
        }

        data = request('POST', self._token_endpoint, data=payload, extra_headers=extra_headers)
        if data is None:
            return None

        new_token, _ = self._consume_token(**data)
        new_token.refresh_token = token.refresh_token  # refresh token should be persistent
        new_token.save()  # will overwrite `token` in db

        return new_token

    def create_auth_url(self, scopes: list[str], extra: dict[str, Any] | None = None) -> str:
        data = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self._redirect_uri,
            'scope': ' '.join(scopes)
        }
        data.update(extra or {})

        return f'{self._auth_endpoint}?{urlencode(data)}'

    def resolve_code(self,
                     code: str,
                     extra_headers: dict[str, str] | None = None
                     ) -> tuple[OAuthToken, dict[str, Any]] | None:
        payload = {
            'grant_type': 'authorization_code',
            'redirect_uri': self._redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code
        }

        data = request('POST', self._token_endpoint, data=payload, extra_headers=extra_headers)
        if data is None:
            return None

        return self._consume_token(**data)

    def get_access_token(self, extra_headers: dict[str, str] | None = None) -> OAuthToken | None:
        try:
            token = OAuthToken.objects.get(service=self._provider)
        except OAuthToken.DoesNotExist:
            return None

        if token.expires_at < timezone.now():  # refresh token
            return self._refresh_token(token, extra_headers)
        return token
