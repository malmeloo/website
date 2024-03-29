"""
Django settings for website project.

Generated by 'django-admin startproject' using Django 4.1.6;
Modified by Mike Almeloo (@DismissedGuy)

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import importlib.util
from pathlib import Path

import django_stubs_ext
from django.core.management.utils import get_random_secret_key

from .config import Config

django_stubs_ext.monkeypatch()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = Config(BASE_DIR / 'config.ini')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/
DEBUG = CONFIG.get('server.debug', True)
ALLOWED_HOSTS = CONFIG.get('server.allowedHosts', [])

SECRET_KEY = 'django-insecure'
if not DEBUG:
    try:
        with (BASE_DIR / 'secret.key').open('r') as f:
            SECRET_KEY = f.read().strip()
        print('KEY: Loaded from disk')
    except (FileNotFoundError, IOError):
        SECRET_KEY = get_random_secret_key()
        with (BASE_DIR / 'secret.key').open('w+') as f:
            f.write(SECRET_KEY)
        print('KEY: Generated and saved to disk')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'compressor',

    'apps.home',
    'apps.api'
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'website.urls'

# Template engines
# https://docs.djangoproject.com/en/4.1/topics/templates/#configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ]
        },
    },
]

WSGI_APPLICATION = 'website.wsgi.application'

# Database
# Use SQLite3 in testing and psql + config.ini settings in prod
#
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3'
    } if DEBUG else {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': CONFIG.get('server.database.host', '127.0.0.1'),
        'PORT': CONFIG.get('server.database.port', '5432'),
        'NAME': CONFIG.get('server.database.name'),
        'USER': CONFIG.get('server.database.user'),
        'PASSWORD': CONFIG.get('server.database.password'),
    }
}

# Cache
# Use memcached in prod, database table in dev
#
# https://docs.djangoproject.com/en/4.1/topics/cache/
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache',
    } if DEBUG else {
        'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
        'LOCATION': 'unix:/tmp/memcached.sock',
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'static'

# Django-compress + libsass + purgecss
# https://django-compressor.readthedocs.io/en/3.1/
# https://github.com/torchbox/django-libsass
COMPRESS_ENABLED = True
PURGECSS_SAFELIST = ['spinning', 'fa-spinner', 'fa-play', 'fa-pause']

COMPRESS_OFFLINE = not CONFIG.get('server.debug', True)
COMPRESS_OUTPUT_DIR = 'compressed'
LIBSASS_ADDITIONAL_INCLUDE_PATHS = [str(STATIC_ROOT)]
COMPRESS_REBUILD_TIMEOUT = 1 if DEBUG else 60 * 60 * 24 * 30  # always rebuild in debug mode
COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)
COMPRESS_FILTERS = {
    'css': [
        'website.purgecss.PurgeCSSFilter',
        'compressor.filters.cssmin.rCSSMinFilter'
    ],
    'js': [
        'compressor.filters.jsmin.rJSMinFilter'
    ]
}
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
LIBSASS_OUTPUT_STYLE = 'compressed'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
