from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse

from apps.api.models import SpotifyStateCode
from . import spotify_api

ALLOWED_EMAILS = settings.CONFIG.get('spotify.allowedEmails')


def login(request: HttpRequest):
    if not spotify_api.can_operate():
        return HttpResponse('Error: clientId or clientSecret is missing, update config!', status=500)

    url = spotify_api.get_callback_url(
        request.build_absolute_uri(reverse(callback)),
        SpotifyStateCode.generate().state_code
    )
    return redirect(url)


def callback(request: HttpRequest):
    if not spotify_api.can_operate():
        return HttpResponse('Error: clientId or clientSecret is missing, update config!', status=500)

    state = request.GET.get('state')
    if state is None or not SpotifyStateCode.verify(state):
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
    token = spotify_api.resolve_access_token(code, request.build_absolute_uri().split('?')[0])
    if token is None:
        # 500 internal server error
        return HttpResponse('Error while retrieving or decoding authentication token', status=500)

    profile = spotify_api.get_user_profile(token)
    if profile is None:
        # 500 internal server error
        return HttpResponse('Error: could not retrieve account details', status=500)
    email = profile.get('email', '<unknown>')

    if email not in ALLOWED_EMAILS:
        # 403 forbidden
        return HttpResponse(f'Error: account is not in the allowlist (logged in as {email})', status=403)

    token.save()
    return HttpResponse(f'Done! Logged in as: {profile["email"]}')


def get_top_songs(request: HttpRequest):
    token = spotify_api.get_access_token()
    if token is None:
        # 503 service unavailable
        return JsonResponse({'error': 'account unlinked, ask administrator to log in'}, status=503)

    songs = spotify_api.get_top_songs(token)
    if songs is None:
        # 503 service unavailable
        return JsonResponse({'error': 'error while communicating with spotify'}, status=503)

    tracks = []
    for item in songs.get('items', []):
        artists = [{
            'name': artist.get('name', '<unknown>'),
            'url': artist.get('external_urls', {}).get('spotify', None)
        } for artist in item.get('artists', [])]
        images = item.get('album', {}).get('images', [])

        tracks.append({
            'name': item.get('name', '<unknown>'),
            'url': item.get('external_urls', {}).get('spotify', None),
            'cover': images[0].get('url', None) if images else None,
            'artists': artists,
            'preview_url': item.get('preview_url', None)
        })

    return JsonResponse({'tracks': tracks})
