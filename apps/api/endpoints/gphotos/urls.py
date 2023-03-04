from django.urls import path

from .views import login, callback, get_albums, get_image

urlpatterns = [
    path('login', login),
    path('callback', callback),
    path('albums', get_albums),
    path('image', get_image)
]
