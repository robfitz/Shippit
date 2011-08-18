from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',


    ('^$', 's_stream.views.stream'),

    ('^project/(?P<project_id>[0-9]*)/$', 's_projects.views.project_info'),
    ('^blurb/(?P<update_id>[0-9]*)/$', 's_stream.views.update_info'),
    ('^user/(?P<username>[-_ !@\'a-zA-Z0-9]*)/$', 's_users.views.user_info'),


    ('^subscribe/(?P<subscription_title>[a-zA-Z ]*)/$', 's_broadcast.views.subscribe'),

    ('^ah/warmup$', 'djangoappengine.views.warmup'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    ('', 'django.views.generic.simple.direct_to_template',
     {'template': 'home.html'}),

    #static assets (should be local-only)                   
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': 'media'}),
)
