from django.conf.urls import patterns, url
from channels import views

urlpatterns = patterns('',
    url(r'^(?P<channel_id>\d+)/$', views.index, name='index'),
    url(r'^(?P<channel_id>\d+)/login/', views.log_in,name='login'),
    url(r'^(?P<channel_id>\d+)/logout/', views.log_out,name='logout')
)