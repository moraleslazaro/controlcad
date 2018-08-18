from django.conf.urls import patterns, url
from condis import views


urlpatterns = patterns('',
    url(r'^equip/list/$', views.list_equips, name='condis-equip-list'),
    url(r'^equip/info/(?P<codequipo>[^/]+)/$', views.show_equip_info, name='condis-equip-info')
)