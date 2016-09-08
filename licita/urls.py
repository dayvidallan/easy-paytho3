# -*- coding: utf-8 -*-


from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from newadmin import utils

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^', include('base.urls')),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^base/', include('base.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^newadmin/', include('newadmin.urls'))

)
urlpatterns += [

]

urlpatterns += [
    # Servindo os arquivos estáticos
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT,
        'show_indexes': True,
    }),
    # Servindo os arquivos estáticos
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT,
    })
]
