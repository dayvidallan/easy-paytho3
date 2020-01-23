# -*- coding: utf-8 -*-


from django.conf.urls import include, url

from django.contrib import admin
from django.contrib.auth import login
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
admin.autodiscover()

urlpatterns = [
    url(r'^', include('base.urls')),
    url(r'^accounts/login/$', login),
    url(r'^base/', include('base.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^newadmin/', include('newadmin.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [ url(r'^media/(?P<path>.*)$', serve, { 'document_root': settings.MEDIA_ROOT, }), url(r'^static/(?P<path>.*)$', serve, { 'document_root': settings.STATIC_ROOT }), ]

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         url(r'^__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns


handler500 = 'base.views.erro_500'
handler403 = 'django.views.defaults.permission_denied'
handler404 = 'django.views.defaults.page_not_found'

#handler404 = 'base.views.erro_404'
#handler403 = 'base.views.erro_403'

