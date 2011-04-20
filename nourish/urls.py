from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DetailView
from nourish.views import CreateView
from nourish.views.group import GroupDetailView, GroupJoinView, GroupLeaveView
from nourish.views.event import EventDetailView, EventAttendView, EventGroupView

from nourish.models import Event
from nourish.forms.event import EventForm

from nourish.models import Group
from nourish.forms.group import GroupForm, GroupJoinForm

urlpatterns = patterns('',
    url('^logged-in/$', 'nourish.views.login_redir'),
    url('^register/$', 'nourish.views.register'),
    url('^home/$', 'nourish.views.homepage'),

    url(r'^events/$', ListView.as_view(
        model=Event,
        template_name='nourish/event/list.html',
    )),
    
    url(r'^events/(?P<pk>\d+)/$', EventDetailView.as_view()),
    url(r'^events/(?P<event_id>\d+)(-[^/]+)?/register/guest/$', 'nourish.views.register.event_register_guest'),
    url(r'^events/(?P<pk>\d+)/register/(?P<role>[a-z]+)/$', 'nourish.views.event_register'),
    url(r'^events/(?P<event_id>\d+)(-[^/]+)?/group/(?P<pk>\d+)(-[^/]+)?/$', EventGroupView.as_view()),
    url(r'^events/(?P<event_id>\d+)/group/(?P<event_group_id>\d+)/meals/$', 'nourish.views.event_group_meals'),
    url(r'^events/(?P<event_id>\d+)/group/(?P<event_group_id>\d+)/invite/(?P<host_eg_id>\d+)/$', 'nourish.views.event_group_invite'),
    url(r'^events/(?P<event_id>\d+)/group/(?P<event_group_id>\d+)/invites/$', 'nourish.views.event_group_invites'),
    url(r'^events/(?P<pk>\d+)/attend/$', EventAttendView.as_view()),
    url(r'^zevents/(?P<pk>\d+)/$', DetailView.as_view(
        model=Event,
        template_name='nourish/event/detail.html'
    )),
    url(r'^events/create/$',      CreateView.as_view(
        form_class=EventForm, 
        template_name='nourish/event/form.html'
    )),

    url(r'^groups/$', ListView.as_view(
        model=Group,
        template_name='nourish/group/list.html',
    )),
    url(r'^groups/(?P<pk>\d+)/$', GroupDetailView.as_view()),
    url(r'^groups/(?P<pk>\d+)/join/$', GroupJoinView.as_view()),
    url(r'^groups/(?P<pk>\d+)/leave/$', GroupLeaveView.as_view()),
    url(r'^groups/create/(?P<type>[a-z]+)?$',      CreateView.as_view(
        form_class=GroupForm, 
        template_name='nourish/group/form.html'
    )),
)
