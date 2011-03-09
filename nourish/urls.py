from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DetailView
from nourish.views import CreateView
from nourish.models import Event
from nourish.forms.event import EventForm

urlpatterns = patterns('',
    url(r'^events/$', ListView.as_view(model=Event)),
    url(r'^events/(?P<pk>\d+)/$', DetailView.as_view(
        model=Event,
        template_name='nourish/event_detail.html'
    )),
    url(r'^events/create/$',      CreateView.as_view(
        form_class=EventForm, 
        template_name='nourish/event_form.html'
    )),
    url('^home/$', 'nourish.views.homepage'),
)
