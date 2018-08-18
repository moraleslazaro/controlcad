from django.conf.urls import patterns, url
from cad import views


urlpatterns = patterns('',
    # Site root
    url(r'^$', views.start_view, name='cad-docroot'),

    # Draw's urls.
    url(r'^cad/list/$', views.list_draws, name='cad-list'),
    url(r'^cad/list/inbox/$', views.list_draws_inbox, name='cad-list-inbox'),
    url(r'^cad/list/public/$', views.list_draws_public, name='cad-list-public'),
    url(r'^cad/upload/$', views.upload_dwg, name='cad-upload'),
    url(r'^cad/info/(?P<name>[^/]+)/$', views.show_draw_info, name='cad-show-info'),
    url(r'^cad/versions/(?P<name>[^/]+)/$', views.show_draw_versions, name='cad-show-versions'),
    url(r'^cad/delete/(?P<name>[^/]+)/$', views.delete_draw, name='cad-draw-delete'),
    url(r'^cad/update/(?P<name>[^/]+)/$', views.update_draw, name='cad-draw-update'),

    # DWG's urls.
    url(r'^dwg/delete/(?P<md5>[^/]+)/$', views.delete_dwg, name='cad-dwg-delete'),
    url(r'^dwg/delete/inbox/(?P<md5>[^/]+)/$', views.delete_inbox_dwg, name='cad-inbox-dwg-delete'),
    url(r'^dwg/public/(?P<md5>[^/]+)/$', views.public_dwg, name='cad-dwg-public'),
    url(r'^dwg/(?P<md5>[^/]+)/$', views.download_dwg, name='cad-dwg-download'),

    # Codificator urls
    url(r'^cod/list/$', views.list_codificators, name='cod-list'),
    url(r'^cod/add/$', views.add_codificator, name='cod-add'),
    url(r'^cod/edit/(?P<code>[^/]+)/$', views.edit_codificator, name='cod-edit'),
    url(r'^cod/delete/(?P<code>[^/]+)/$', views.delete_codificator, name='cod-delete')
)