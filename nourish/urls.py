from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DetailView

from nourish.views import GroupDetailView, EventDetailView, EventGroupView
from nourish.models import Event, Group

urlpatterns = patterns('',
    url('^logged-in/$', 'nourish.views.homepage_chooser'),
    url('^register/event/$', 'nourish.views.register_event'),
    url('^home/$', 'nourish.views.homepage'),

    url(r'^events/$', ListView.as_view(
        model=Event,
        template_name='nourish/event_list.html',
    )),
    url(r'^events/(?P<pk>\d+)/$', EventDetailView.as_view()),

    url(r'^events/(?P<event_id>\d+)/register/guest/$', 
        'nourish.views.register_event_guest'),
    url(r'^events/\d+/group/(?P<pk>\d+)(-[^/]+)?/$', 
        EventGroupView.as_view()),
    url(r'^events/\d+/group/(?P<pk>\d+)/meals/$', 
        'nourish.views.event_guest_meals'),
    url(r'^events/\d+/group/(?P<pk>\d+)/invite/(?P<host_eg_id>\d+)/$', 
        'nourish.views.event_guest_invite'),
    url(r'^events/\d+/group/(?P<pk>\d+)/invites/$', 
        'nourish.views.event_host_invites'),

    url(r'^groups/$', ListView.as_view(
        model=Group,
        template_name='nourish/group_list.html',
    )),
    url(r'^groups/(?P<pk>\d+)/$', GroupDetailView.as_view()),
)
