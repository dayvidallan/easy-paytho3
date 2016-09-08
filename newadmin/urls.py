
from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^media/$', 'newadmin.views.media', name='media'),
    (r'^chained_select/(?P<app_name>\w+)/(?P<class_name>\w+)/$', 'newadmin.views.chained_select_view'),
)
