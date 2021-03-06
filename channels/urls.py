from django.conf.urls import patterns, url
from channels import views
from django.views.decorators.cache import cache_page

urlpatterns = patterns('',
    url(r'^(?P<channel_id>\d+)/$', views.index, name='index'),
    url(r'^(?P<channel_id>\d+)/login/', views.log_in,name='login'),
    url(r'^(?P<channel_id>\d+)/logout/', views.log_out,name='logout'),
    url(r'^(?P<channel_id>\d+)/update/', cache_page(1)(views.update),name='update'),
    url(r'^(?P<channel_id>\d+)/next/', views.next,name='next'),
    url(r'^(?P<channel_id>\d+)/add/', views.add,name='add'),
    url(r'^(?P<channel_id>\d+)/rm/', views.rm,name='rm'),
    url(r'^(?P<channel_id>\d+)/vote/', views.vote,name='vote'),
    url(r'^(?P<channel_id>\d+)/setbg/', views.set_background,name='setbg'),
    url(r'^(?P<channel_id>\d+)/set_playing/', views.set_playing,name='set_playing'),
    url(r'^(?P<channel_id>\d+)/player/', views.remote_player,name='remote_player'),
)
