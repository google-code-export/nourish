from django.shortcuts import render_to_response, redirect
from nourish.models import EventUser, GroupUser, Group, EventGroup, UserProfile, Event
import array
from django.template import RequestContext
from django.core.urlresolvers import reverse

def homepage(request):
    groups = [ ]
    events = []
    if request.user.is_authenticated():
        for gm in GroupUser.objects.filter(user=request.user):
            groups.append(gm.group)

        egs = list(EventGroup.objects.filter(group__in=groups))

        for eu in EventUser.objects.filter(user=request.user):
            events.append(eu.event)
    else:
        egs = None

    return render_to_response('nourish/homepage.html', { 
        'request': request,
        'events' : events,
        'egs' : egs,
        'groups' : groups,
    }, context_instance=RequestContext(request))

def rootpage(request):
    events = Event.objects.filter(display=True)

    return render_to_response('nourish/rootpage.html', { 
        'request': request,
        'events' : events,
    }, context_instance=RequestContext(request))

def homepage_chooser(request):
    url = homepage_chooser_url(request)
    return redirect(url)

def homepage_chooser_url(request):
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
