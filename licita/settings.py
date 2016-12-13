# coding: utf-8

import os
from os.path import abspath, dirname

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = abspath(dirname(dirname(__file__)))
SECRET_KEY = '0$p#v)*(zb22za#6c=7yg$=$v-7xh8w7zf2gbd9*mezlsr*3*o'
DEBUG = True
TEMPLATE_DEBUG = True

INSTALLED_APPS = (


    # Third party apps
    'newadmin',
    'localflavor',
    'bootstrapform',
    'bootstrap3_datetime',
    'django_extensions',
    'compressor',
    'dal',
    'dal_select2',
    'ckeditor',
    # Django apps
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # 'debug_toolbar',

    # Local apps
    'base',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'licita.urls'

WSGI_APPLICATION = 'licita.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'licita',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'licita',
        'USER': 'walkyso',
        'PASSWORD': 'licitaeasy',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}


LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Recife'
USE_I18N = True
USE_L10N = True
USE_TZ = False
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Django settings changed

INTERNAL_IPS = ('127.0.0.1',)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
TEMPLATE_DIRS = (BASE_DIR,)
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'
DATE_INPUT_FORMATS = ('%d/%m/%Y',)
DATETIME_INPUT_FORMATS = ('%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M',)
#SESSION_COOKIE_AGE = 60 * 10  # The age of session cookies, in seconds.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',  # builtin
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',  # builtin
    'compressor.finders.CompressorFinder',
)

LOGIN_URL = '/admin/login/'

AUTH_USER_MODEL = 'base.User'




THUMB_SIZE = (100,100)

# Definindo o padrão de mensagem de erro para seguir o do Bootstrap 3.
from django.contrib import messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}



PDF_SIGNER_DIR = os.path.join(BASE_DIR, 'telediagnostico/assinatura_digital/portable_signer/')
SYSTEM_CERTIFICATE_PATH = os.path.join(BASE_DIR, 'telediagnostico/assinatura_digital/certificados/certificate.pfx')
SYSTEM_PRIVATE_KEY_PASSWORD = 'senha'
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = 'pnt@lais.huol.ufrn.br'

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     },
#     'select2': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': '127.0.0.1:11211',
#     }
# }
#
# SELECT2_CACHE_BACKEND = 'select2'

