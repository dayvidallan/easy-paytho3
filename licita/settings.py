# -*- coding: utf-8 -*-
#pylint: skip-file
"""
Arquivo modelo do settings.py.
Aqui deve conter apenas o que há de diferente em relação ao settings_base.py,
como por exemplo senhas e outros dados sigilosos.
"""

try:
    from settings_base import *
except ImportError, e:
    pass

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
