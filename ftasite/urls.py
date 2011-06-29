from django.conf.urls.defaults import patterns, include, url
from django.contrib.auth.views import login, logout
from django.views.generic.simple import direct_to_template

from django.contrib import admin
admin.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'

password_reset_dict = { 
    'email_template_name' : 'site/pswd_reset_email.html', 
    'template_name' : 'site/pswd_reset_form.html', 
}

password_reset_confirm_dict = {
    'template_name' : 'site/pswd_reset_confirm.html', 
    'post_reset_redirect':'/login/', 
}

urlpatterns = patterns('',
    url(r'^nourish/', include('nourish.urls')),
    url(r'^nourish/fb/', include('nourish.urls', namespace='fbcanvas'), { 'fbcanvas' : True }),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^social/', include('socialregistration.urls')),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^reset/$', 'django.contrib.auth.views.password_reset', password_reset_dict),
    url(r'^reset/conf/(?P<uidb64>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'django.contrib.auth.views.password_reset_confirm', password_reset_confirm_dict),
    url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name':'site/pswd_reset_done.html'}),
    url(r'^reset/complete$', 'django.contrib.auth.views.password_reset_complete'),
    (r'^donate/$', direct_to_template, {'template': 'site/donate.html'}),
    (r'^$', direct_to_template, {'template': 'site/home.html'}),
    (r'^video/$', direct_to_template, {'template': 'site/video.html'}),
    (r'^archives/$', direct_to_template, {'template': 'site/archives.html'}),
)
