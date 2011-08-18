from django.conf.urls.defaults import patterns, url
from django.contrib.auth.decorators import login_required
from django.views.generic.simple import direct_to_template

from django.views.generic import DetailView

from nourish.views.group import GroupDetailView, GroupUpdateView, GroupListView
from nourish.views.event import EventDetailView, EventGroupView, EventUpdateView, EventListView, EventGroupUpdateView, EventSummaryView, EventGroupsView, EventGroupReportsView
from nourish.views.notification import NotificationListView 
from nourish.views.homepage import RootPageView, HomePageView
from nourish.views.register.event import EventRegisterView
from nourish.views.register.guest import EventGuestRegisterView
from nourish.views.register.host import EventHostRegisterView
from nourish.views.register.host_invite import EventHostInviteView
from nourish.views.meal import EventGuestManageView, EventArtistChart, EventReports, ConfirmInviteView
from fbcanvas.views import CanvasTemplateView
from nourish.models import Event, Group, EventGroup

urlpatterns = patterns('',
    url('^logged-in/$', 'nourish.views.homepage_chooser', name='homepage-chooser'),
    url('^register/event/$', EventRegisterView.as_view(), name='register-event'),
    url('^home/$', login_required(HomePageView.as_view()), name='homepage'),
    url('^confirm_invite/$', ConfirmInviteView.as_view(), name='confirm-invite'),
    url('^$',      RootPageView.as_view(), name='rootpage'),

    url(r'^_notif/$', login_required(NotificationListView.as_view()), name='notification-list'),
    url(r'^events/$', EventListView.as_view(), name='event-list'),

    url(r'^e/(?P<pk>\d+)-(?P<slug>[^\/]*)/$', EventDetailView.as_view(), name='event-detail'),
    url(r'^e/(?P<pk>\d+)-(?P<slug>[^\/]*)/summary/$', EventSummaryView.as_view(), name='event-summary'),
    url(r'^e/(?P<pk>\d+)-(?P<slug>[^\/]*)/groups/$', EventGroupsView.as_view(), name='event-groups'),
    url(r'^e/(?P<pk>\d+)-(?P<slug>[^\/]*)/invite/$', EventHostInviteView.as_view(), name='event-invite'),
    url(r'^e/(?P<pk>\d+)(-[^\/]*)?/edit/$', login_required(EventUpdateView.as_view())),

    url(r'^e/(?P<pk>\d+)(-[^\/]*)?/register/guest/$', 
        EventGuestRegisterView.as_view()),
    url(r'^e/(?P<pk>\d+)(-[^\/]*)?/register/host/$', 
        EventHostRegisterView.as_view()),
    url(r'^e/(?P<pk>\d+)(-[^\/]*)?/artistchart/$', 
        EventArtistChart.as_view()),
    url(r'^e/(?P<pk>\d+)(-[^\/]*)?/reports/$',
        EventReports.as_view()),
    url(r'^eg/(?P<pk>\d+)-(?P<slug>[^/]+)/$', 
        EventGroupView.as_view(), name='event-group-detail'),

    url(r'^eg/(?P<pk>\d+)-(?P<slug>[^/]+)/confirmation/$',
        DetailView.as_view(
          model=EventGroup,
          template_name='nourish/event_group_confirmation.html'),
        name='event-group-confirmation'),

    url(r'^eg/(?P<pk>\d+)(-[^\/]*)?/edit/$', 
        EventGroupUpdateView.as_view(), name='event-group-edit'),
    url(r'^eg/(?P<pk>\d+)(-[^\/]*)?/meals/$', 
        EventGuestManageView.as_view(), name='event-guest-manage'),
    url(r'^eg/(?P<pk>\d+)(-[^\/]*)?/reports/$', 
        EventGroupReportsView.as_view(), name='event-group-reports'),

    url(r'^groups/$', GroupListView.as_view(), name='group-list'),
    url(r'^g/(?P<pk>\d+)-(?P<slug>[^\/]*)/$', GroupDetailView.as_view(), name='group-detail'),
    url(r'^g/(?P<pk>\d+)(-[^\/]*)?/edit/$', login_required(GroupUpdateView.as_view())),

    url(r'^fb_newgroup_options/$', CanvasTemplateView.as_view(template_name="nourish/fb_newgroup_options_page.html"), name='fb-newgroup-options'),
)
