
from django.conf.urls import url
from django.contrib import admin
from newadmin.views import chained_select_view, media

admin.autodiscover()

urlpatterns = [
    url(r'^media/$', media, name='media'),
    url(r'^chained_select/(?P<app_name>\w+)/(?P<class_name>\w+)/$', chained_select_view),
]
