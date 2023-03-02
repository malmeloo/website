from django.urls import include, path

from .endpoints.gphotos import urls as gphotos_urls
from .endpoints.spotify import urls as spotify_urls

urlpatterns = [
    path('spotify/', include(spotify_urls.urlpatterns)),
    path('gphotos/', include(gphotos_urls.urlpatterns))
]
