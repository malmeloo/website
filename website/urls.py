"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from apps.api import urls as api_urls
from apps.home import urls as home_urls
from apps.wellknown import urls as wk_urls

urlpatterns = [
    path('.well-known/', include(wk_urls.urlpatterns)),

    path('admin/', admin.site.urls),

    path('api/', include(api_urls.urlpatterns)),
    path('', include(home_urls.urlpatterns))
]
