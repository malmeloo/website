from django.urls import include, path

from .endpoints.spotify import urls as spotify_urls

urlpatterns = [
    path('spotify/', include(spotify_urls.urlpatterns)),
]
