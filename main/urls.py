from django.conf.urls import patterns, url
from main import views
from django.views.decorators.cache import cache_page

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
