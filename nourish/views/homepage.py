from django.shortcuts import render_to_response, redirect
from nourish.models import EventUser, GroupUser, Group, EventGroup, UserProfile, Event
import array
from django.template import RequestContext

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
    events = Event.objects.all()

    return render_to_response('nourish/rootpage.html', { 
        'request': request,
        'events' : events,
    }, context_instance=RequestContext(request))

def homepage_chooser(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return redirect('/home')
    if profile.role == 'E':
        eus = EventUser.objects.filter(user=user,admin=True)
        if len(eus) > 1:
            return redirect('/home')
        if not len(eus):
            return redirect('/register/event/')
        return redirect(eu.event.get_absolute_url())
    if profile.role == 'T':
        gus = GroupUser.objects.filter(user=user,admin=True)
        if len(gus) > 1:
            return redirect('/home')
        if not len(gus):
            return redirect('/groups/create?host')
        egs = EventGroup.objects.filter(group=gus[0].group)
        if len(egs) == 1:
            return redirect(egs[0].get_absolute_url())
        return redirect('/home')
    if profile.role == 'A':
        gus = GroupUser.objects.filter(user=user,admin=True)
        if len(gus) > 1:
            return redirect('/home')
        if not len(gus):
            if 'nourish_event' in request.session:
                event = Event.objects.get(id = request.session['nourish_event'])
                return redirect(event.get_absolute_url() + 'register/guest/')
            return redirect('/events/')
        egs = EventGroup.objects.filter(group=gus[0].group)
        if len(egs) == 1:
            return redirect(egs[0].get_absolute_url())
        return redirect('/home')
    return redirect('/home')
