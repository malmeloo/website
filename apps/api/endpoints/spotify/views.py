import base64
import random
import string
from datetime import datetime
from urllib.parse import urlencode

import httpx
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse

CLIENT_ID = settings.CONFIG.get('spotify.clientId')
CLIENT_SECRET = settings.CONFIG.get('spotify.clientSecret')
ALLOWED_EMAILS = settings.CONFIG.get('spotify.allowedEmails')

HEADERS = {
    'Authorization': 'Basic ' + base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()
}

TOKEN_URL = 'https://accounts.spotify.com/api/token'
AUTHORIZE_CALLBACK = 'https://accounts.spotify.com/authorize'
SCOPES = 'user-read-private user-read-email'

client = httpx.Client()


# In-memory state tracker. Provides protection against XSS during the authorization flow.
class StateTracker:
    STATE_TIMEOUT = settings.CONFIG.get('spotify.authorizeTimeout', 60 * 60)
    STATE_SIZE = 16

    def __init__(self):
        self._state_codes = {}

    def _get_state_code(self):
        # technically not cryptographically secure, but that's not too important here
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(self.STATE_SIZE))

    def _clean(self):
        """Remove expired state codes"""
        now = datetime.now()
        to_remove = set()
        for state, exp in self._state_codes.items():
            if (now - exp).seconds > self.STATE_TIMEOUT:
                to_remove.add(state)

        for state in to_remove:
            del self._state_codes[state]

    def generate(self):
        """Generates, saves and returns a new state code."""
        self._clean()

        state = self._get_state_code()
        self._state_codes[state] = datetime.now()

        return state

    def verify(self, state_code: string):
        """Verifies a given state code against the ones that are saved.
        Deletes the state from memory if found."""
        self._clean()

        expiry = self._state_codes.get(state_code)
        if expiry is None:
            return False

        del self._state_codes[state_code]
        return True


states = StateTracker()


def login(request: HttpRequest):
    if CLIENT_ID is None or CLIENT_SECRET is None:
        return HttpResponse('Error: clientId or clientSecret is missing, update config!', status=500)

    qs = urlencode({
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPES,
        'redirect_uri': request.build_absolute_uri(reverse(callback)),
        'show_dialog': True,
        'state': states.generate()
    })
    return redirect(AUTHORIZE_CALLBACK + '?' + qs)


def callback(request: HttpRequest):
    state = request.GET.get('state')
    if state is None or not states.verify(state):
        # 400 bad request
        return HttpResponse('Error: missing or invalid state parameter', status=400)

    error = request.GET.get('error')
    if error is not None:
        # 503 service unavailable
        return HttpResponse(f'Spotify error: {error}', status=503)

    code = request.GET.get('code')
    if code is None:
        # 400 bad request
        return HttpResponse('Error: missing code parameter', status=400)

    # exchange code for token
    try:
        r = client.post(TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': request.build_absolute_uri().split('?')[0]
        }, headers=HEADERS)
        print(r.json())
    except (httpx.RequestError, httpx.DecodingError):
        # 500 internal server error
        return HttpResponse('Error while retrieving or decoding authentication token', status=500)

    return HttpResponse(f'Done! Code: ' + code)
