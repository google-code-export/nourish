from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout

from django.contrib import admin
admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

urlpatterns = patterns('',
    url(r'^nourish/', include('nourish.urls')),
    url(r'^nourish/fb/', include('nourish.urls', namespace='canvas'), { 'canvas' : True }),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^social/', include('socialregistration.urls')),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
)