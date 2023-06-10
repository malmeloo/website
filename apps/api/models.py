import random
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone


class OAuthToken(models.Model):
    service = models.CharField(primary_key=True, max_length=20)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    scope = models.CharField(max_length=100)
    expires_at = models.DateTimeField()

    def __str__(self) -> str:
        return self.service


class TempStateCode(models.Model):
    domain = models.CharField(max_length=32)
    state_code = models.CharField(max_length=16)
    expires_at = models.DateTimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['domain', 'state_code'], name='unique_domain_state')
        ]

    def __str__(self) -> str:
        return f'{self.domain} - {self.state_code}'

    @classmethod
    def _clean(cls) -> None:
        cls.objects.filter(expires_at__lt=timezone.now()).delete()

    @classmethod
    def generate(cls, domain: str, expires_in: int = 3600) -> 'TempStateCode':
        cls._clean()

        code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        state = cls(
            domain=domain,
            state_code=code,
            expires_at=timezone.now() + timedelta(seconds=expires_in)
        )
        state.save()

        return state

    @classmethod
    def verify(cls, domain: str, code: str) -> bool:
        cls._clean()

        codes = cls.objects.filter(domain=domain, state_code=code)
        try:
            return codes.exists()
        finally:
            codes.delete()
