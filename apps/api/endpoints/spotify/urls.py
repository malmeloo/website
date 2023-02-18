from django.urls import path

from .views import login, callback, get_top_songs

urlpatterns = [
    path('login', login),
    path('callback', callback),

    path('songs/top', get_top_songs)
]
