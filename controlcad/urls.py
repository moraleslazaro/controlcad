from django.conf.urls import patterns, url, include


urlpatterns = patterns('',
    url(r'^', include('cad.urls')),
    url(r'^', include('scan.urls')),
    url(r'^', include('admin.urls')),
    url(r'^', include('condis.urls'))
)
