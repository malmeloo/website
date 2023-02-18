from django.db import models


class SpotifyStateCode(models.Model):
    state_code = models.CharField(max_length=30)
    expires_at = models.DateTimeField()
