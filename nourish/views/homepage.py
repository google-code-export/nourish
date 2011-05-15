from django.shortcuts import redirect
from nourish.models import EventUser, GroupUser, Group, EventGroup, UserProfile, Event
from django.core.urlresolvers import reverse
from django.views.generic import TemplateView
from fbcanvas.views import HybridCanvasView
import re

class RootPageView(HybridCanvasView, TemplateView):
    template_name = "nourish/rootpage.html"

    def get_context_data(self, **kwargs):
        context = super(RootPage, self).get_context_data(**kwargs)
        context['events'] = Event.objects.filter(display=True)
        return context

    def get(self, request, *args, **kwargs):
        if 'fbcanvas' in kwargs and kwargs['fbcanvas']:
            if 'request_ids' in request.GET:
                return redirect('/nourish/fb/_notif/?request_ids=' + request.GET['request_ids'])
            if 'ref' in request.GET and request.GET['ref'] == 'bookmarks':
                if 'count' in request.GET and request.GET['count']:
                    return redirect('/nourish/fb/_notif/?last=%s&ref=bookmarks' % request.GET['count'])
                return redirect('/nourish/fb/home/')
        return super(RootPage, self).get(request, **kwargs)

class HomePageView(HybridCanvasView, TemplateView):
    template_name = "nourish/homepage.html"

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)

        context['groups'] = [ ]
        context['events'] = []
        context['egs'] = []

        if self.request.user.is_authenticated():
            for gm in GroupUser.objects.filter(user=self.request.user):
                context['groups'].append(gm.group)

            context['egs'] = list(EventGroup.objects.filter(group__in=context['groups']))
    
            for eu in EventUser.objects.filter(user=self.request.user):
                context['events'].append(eu.event)

        return context

def homepage_chooser(request, fbcanvas=False):
    url = homepage_chooser_url(request, fbcanvas)
    if fbcanvas:
        p = re.compile("\/nourish\/")
        url = p.sub('/nourish/fb/', url)
    return redirect(url)

def homepage_chooser_url(request, fbcanvas=False):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.role == 'E':
            eus = EventUser.objects.filter(user=user,admin=True)
            if len(eus) > 1:
                return reverse('homepage')
            if not len(eus):
                return reverse('register-event')
            return eus[0].event.get_absolute_url()
        if profile.role == 'T':
            gus = GroupUser.objects.get(user=user,admin=True)
            egs = EventGroup.objects.get(group=gus[0].group)
            return egs[0].get_absolute_url()
        if profile.role == 'A':
            gus = GroupUser.objects.filter(user=user,admin=True)
            if len(gus) > 1:
                return reverse('homepage')
            if not len(gus):
                if 'nourish_event' in request.session:
                    event = Event.objects.get(id = request.session['nourish_event'])
                    return event.get_absolute_url() + 'register/guest/'
                return reverse('event-list')
            egs = EventGroup.objects.get(group=gus[0].group)
            return egs[0].get_absolute_url()
    except:
        return reverse('homepage')
    return reverse('homepage')
