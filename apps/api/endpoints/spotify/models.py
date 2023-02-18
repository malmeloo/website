import random
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone


class SpotifyStateCode(models.Model):
    state_code = models.CharField(primary_key=True, max_length=16)
    expires_at = models.DateTimeField()

    @classmethod
    def _clean(cls):
        cls.objects.filter(expires_at__lt=timezone.now()).delete()

    @classmethod
    def generate(cls, expires_in: int = 3600):
        cls._clean()

        code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        state = cls(
            state_code=code,
            expires_at=timezone.now() + timedelta(seconds=expires_in)
        )
        state.save()

        return state

    @classmethod
    def verify(cls, code: string):
        cls._clean()

        codes = cls.objects.filter(state_code=code)
        if not codes.exists():
            return False
        codes.delete()
        return True
