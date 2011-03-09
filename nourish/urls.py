from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DetailView
from nourish.views import CreateView
from nourish.views.group import GroupDetailView, GroupUserView

from nourish.models import Event
from nourish.forms.event import EventForm

from nourish.models import Group
from nourish.forms.group import GroupForm, GroupUserForm

urlpatterns = patterns('',
    url('^home/$', 'nourish.views.homepage'),

    url(r'^events/$', ListView.as_view(
        model=Event,
        template_name='nourish/event/list.html',
    )),
    url(r'^events/(?P<pk>\d+)/$', DetailView.as_view(
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
    url(r'^groups/(?P<pk>\d+)/join/$', CreateView.as_view(
	form_class=GroupUserForm,
        template_name='nourish/group/user_form.html'
    )),
    url(r'^groups/create/$',      CreateView.as_view(
        form_class=GroupForm, 
        template_name='nourish/group/form.html'
    )),
)
