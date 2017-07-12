# -*- coding: utf-8 -*-


from django.conf.urls import include, url

from django.contrib import admin
from django.contrib.auth.views import login
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
admin.autodiscover()

urlpatterns = [
    url(r'^', include('base.urls')),
    url(r'^accounts/login/$', login),
    url(r'^base/', include('base.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^newadmin/', include('newadmin.urls'))



]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [ url(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT, }), url(r'^static/(?P<path>.*)$', serve, { 'document_root': settings.STATIC_ROOT }), ]


handler500 = 'base.views.erro_500'

handler404 = 'base.views.erro_404'
