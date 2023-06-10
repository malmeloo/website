from django.conf import settings
from django.http import HttpRequest, JsonResponse

MASTODON_USERNAME = settings.CONFIG.get('mastodon.username')
MASTODON_INSTANCE = settings.CONFIG.get('mastodon.instance')


def webfinger(request: HttpRequest) -> JsonResponse:
    return JsonResponse({
        'subject': f'acct:{MASTODON_USERNAME}@{MASTODON_INSTANCE}',
        'aliases': [
            f'https://{MASTODON_INSTANCE}/@{MASTODON_USERNAME}',
            f'https://{MASTODON_INSTANCE}/users/{MASTODON_USERNAME}'
        ],
        'links': [
            {
                'rel': 'http://webfinger.net/rel/profile-page',
                'type': 'text/html',
                'href': f'https://{MASTODON_INSTANCE}/@{MASTODON_USERNAME}'
            },
            {
                'rel': 'self',
                'type': 'application/activity+json',
                'href': f'https://{MASTODON_INSTANCE}/users/{MASTODON_USERNAME}'
            },
            {
                'rel': 'http://ostatus.org/schema/1.0/subscribe',
                'template': f'https://{MASTODON_INSTANCE}/authorize_interaction?uri=' + '{uri}'
            }
        ]
    })
