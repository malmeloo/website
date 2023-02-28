from django.db import models

from .endpoints.spotify.models import SpotifyStateCode


class OAuthToken(models.Model):
    service = models.CharField(primary_key=True, max_length=20)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    scope = models.CharField(max_length=100)
    expires_at = models.DateTimeField()
