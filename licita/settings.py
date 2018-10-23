# coding: utf-8

import os
from os.path import abspath, dirname

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_PATH = abspath(dirname(dirname(__file__)))
SECRET_KEY = '0$p#v)*(zb22za#6c=7yg$=$v-7xh8w12f2gbd9*mezlsr*3*o'
DEBUG = True
ALLOWED_HOSTS = ['*']

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

    # Local apps
    'pagination',
    'base',
    'easyaudit',
    #'debug_toolbar',
    'rest_framework',



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
    'pagination.middleware.PaginationMiddleware',
    'base.middleware.threadlocals.ThreadLocals',
    'easyaudit.middleware.easyaudit.EasyAuditMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
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
#TEMPLATE_DIRS = (BASE_DIR,)
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
#
AUTH_USER_MODEL = 'base.User'


THUMB_SIZE = (100,100)

# Definindo o padrão de mensagem de erro para seguir o do Bootstrap 3.
from django.contrib import messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}





TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.UnsaltedMD5PasswordHasher',
        'django.contrib.auth.hashers.Argon2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        'django.contrib.auth.hashers.BCryptPasswordHasher',
    ]


BOOTSTRAP3 = {
    'form_renderers': {
        'default': 'form_utils_bootstrap3.renderers.BetterFormRenderer'
    }
}




DJANGO_EASY_AUDIT_UNREGISTERED_CLASSES_EXTRA = ['base.MaterialConsumo', ]

DATA_UPLOAD_MAX_NUMBER_FIELDS = None

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    )
}

try:
    from settings_base import *
except ImportError, e:
    pass

SITE_URL = DEBUG and 'http://localhost:8000' or 'http://guamareserver.easygestaopublica.com.br'


