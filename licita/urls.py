# -*- coding: utf-8 -*-


from django.conf.urls import include, url

from django.contrib import admin
from django.contrib.auth.views import login
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = [
    url(r'^', include('base.urls')),
    url(r'^accounts/login/$', login),
    url(r'^base/', include('base.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^newadmin/', include('newadmin.urls'))



]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += [
#     # Servindo os arquivos estáticos
#     url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
#         'document_root': settings.STATIC_ROOT,
#         'show_indexes': True,
#     }),
#     # Servindo os arquivos estáticos
#     url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
#         'document_root': settings.MEDIA_ROOT,
#     })
# ]
