from django.contrib import admin

from .models import OAuthToken, TempStateCode


@admin.register(OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    list_display = ('service', 'expires_at', 'scope')


@admin.register(TempStateCode)
class TempStateCodeAdmin(admin.ModelAdmin):
    list_display = ('domain', 'expires_at', 'state_code')
