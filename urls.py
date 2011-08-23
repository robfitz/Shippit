from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',


    ('^$', 's_stream.views.stream'),

    # ajax loads for info panel
    ('^project/(?P<project_id>[0-9]*)/$', 's_projects.views.project_info'),
    ('^blurb/(?P<update_id>[0-9]*)/$', 's_stream.views.update_info'),
    ('^user/(?P<username>[-_ !@\'a-zA-Z0-9]*)/$', 's_users.views.user_info'), 

    ('^project/new/$', 's_projects.views.project_info'),
    ('^blurb/new/$', 'django.views.generic.simple.direct_to_template', {'template': 'new_blog.html'}),

    ('^blurb/publish/(?P<update_id>[0-9]*)/$', 's_stream.views.publish_unconfirmed'),
    ('^blurb/discard/(?P<update_id>[0-9]*)/$', 's_stream.views.discard_unconfirmed'),
    
    ('^about/', 'django.views.generic.simple.direct_to_template', {'template': 'about.html'}),

    ('^subscribe/(?P<subscription_title>[a-zA-Z ]*)/$', 's_broadcast.views.subscribe'),

    ('^ah/warmup$', 'djangoappengine.views.warmup'),

    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),

    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
    (r'^accounts/logout/$', 
        'django.contrib.auth.views.logout',
        { 'next_page': '/' }),
    (r'^accounts/register/$', 's_users.views.register'),

    (r'^accounts/request_invite/$', 's_users.views.request_invite'),
    (r'^accounts/reject_invite/$', 's_users.views.reject_invite'),

    #static assets (should be local-only)                   
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
         {'document_root': 'media'}),
    (r'^uploads/(?P<id>.*)$', 's_media.views.get_uploaded_image'),
)
