from django.conf.urls import url, patterns


urlpatterns = patterns('',
    # User toolbox
    url(r'^login/$', 'admin.views.login', name='login'),
    url(r'^logout/$', 'admin.views.logout', name='logout'),
    url(r'^account/password/$', 'admin.views.logged_user_change_password', name='logged-user-change-password'),
    url(r'^account/$', 'admin.views.logged_user_account_info', name='logged-user-account-info'),

    # Admin CPanel
    url(r'^admin/users/list/$', 'admin.views.admin_user_list', name='admin-user-list'),
    url(r'^admin/users/add/$', 'admin.views.admin_user_add', name='admin-user-add'),
    url(r'^admin/users/edit/(?P<id>[^/]+)/$', 'admin.views.admin_user_edit', name='admin-user-edit'),
    url(r'^admin/users/password/(?P<id>[^/]+)/$', 'admin.views.admin_user_change_password', name='admin-user-change-password'),
    url(r'^admin/users/delete/(?P<username>[^/]+)/$', 'admin.views.admin_user_delete', name='admin-user-delete'),
    url(r'^admin/dashboard/$', 'admin.views.admin_show_dashboard', name='admin-dashboard')
)
