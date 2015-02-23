from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$',include('main.urls',namespace="main")),
    url(r'^channels/',include('channels.urls',namespace="channels"))
)
