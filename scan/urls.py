from django.conf.urls import patterns, url
from scan import views


urlpatterns = patterns('',
    # Single draws.
    url(r'^scan/single/list/$', views.list_single, name='scan-single-list'),
    url(r'^scan/single/upload/$', views.upload_single, name='scan-single-upload'),
    url(r'^scan/single/delete/(?P<filename>[^/]+)/$', views.delete_single, name='scan-single-delete'),
    url(r'^scan/single/update/(?P<number>[^/]+)/$', views.update_single, name='scan-single-update'),
    url(r'^scan/single/info/(?P<number>[^/]+)/$', views.show_single_info, name='scan-single-info'),
    url(r'^scan/single/preview/(?P<number>[^/]+)/$', views.show_single_preview, name='scan-single-show'),
    url(r'^scan/single/print/(?P<number>[^/]+)/$', views.print_single, name='scan-single-print'),
    # Inline and attachment HTTP responses for single draws.
    url(r'^scan/single/inline/(?P<filename>[^/]+)/$', views.single_inline, name='scan-single-preview'),
    url(r'^scan/single/download/(?P<filename>[^/]+)/$', views.single_download, name='scan-single-download'),

    # Relation draws.
    url(r'^scan/relation/list/$', views.list_relation, name='scan-relation-list'),
    url(r'^scan/relation/upload/$', views.upload_relation, name='scan-relation-upload'),
    url(r'^scan/relation/delete/(?P<filename>[^/]+)/$', views.delete_relation, name='scan-relation-delete'),
    url(r'^scan/relation/update/(?P<code>[^/]+)/$', views.update_relation, name='scan-relation-update'),
    url(r'^scan/relation/info/(?P<code>[^/]+)/$', views.show_relation_info, name='scan-relation-info'),
    url(r'^scan/relation/preview/(?P<code>[^/]+)/$', views.show_relation_preview, name='scan-relation-show'),
    url(r'^scan/relation/related-schema/(?P<code>[^/]+)/$', views.show_relation_schema, name='scan-relation-schema'),
    url(r'^scan/relation/print/(?P<code>[^/]+)/$', views.print_relation, name='scan-relation-print'),
    # Inline and attachment HTTP responses for single draws.
    url(r'^scan/relation/inline/(?P<filename>[^/]+)/$', views.relation_inline, name='scan-relation-preview'),
    url(r'^scan/relation/download/(?P<filename>[^/]+)/$', views.relation_download, name='scan-relation-download'),


    # Schema draws.
    url(r'^scan/schema/list/$', views.list_schema, name='scan-schema-list'),
    url(r'^scan/schema/upload/$', views.upload_schema, name='scan-schema-upload'),
    url(r'^scan/schema/delete/(?P<filename>[^/]+)/$', views.delete_schema, name='scan-schema-delete'),
    url(r'^scan/schema/update/(?P<reference>[^/]+)/$', views.update_schema, name='scan-schema-update'),
    url(r'^scan/schema/info/(?P<reference>[^/]+)/$', views.show_schema_info, name='scan-schema-info'),
    url(r'^scan/schema/preview/(?P<reference>[^/]+)/$', views.show_schema_preview, name='scan-schema-show'),
    url(r'^scan/schema/print/(?P<reference>[^/]+)/$', views.print_schema, name='scan-schema-print'),
    # Inline and attachment HTTP responses for single draws.
    url(r'^scan/schema/inline/(?P<filename>[^/]+)/$', views.schema_inline, name='scan-schema-preview'),
    url(r'^scan/schema/download/(?P<filename>[^/]+)/$', views.schema_download, name='scan-schema-download'),
)
