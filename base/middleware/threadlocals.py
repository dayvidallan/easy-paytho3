# -*- coding: utf-8 -*-

"""
In settings.py, MIDDLEWARE_CLASSES:
'<project_name>.djtools.middleware.threadlocals.ThreadLocals'

To import:
from <project_name>.djtools.middelware import threadlocals as tl
"""

from threading import local

def get_client_ip(request):
    for attr in ('HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR'):
        if request.META.get(attr):
            return request.META.get(attr)


tl = local()

def get_request():
    return getattr(tl, 'request', None)

def get_user():
    return getattr(tl, 'user', None)

def get_profile():
    try:
        return get_user().get_profile()
    except:
        return None

def get_remote_addr():
    request = get_request()
    if request:
        return get_client_ip(request)
    return None

class ThreadLocals(object):
    def process_request(self, request):
        tl.user = getattr(request, 'user', None)
        tl.request = request
