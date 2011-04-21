from django.shortcuts import render_to_response, redirect
from nourish.models import EventUser, GroupUser, Group, EventGroup, UserProfile
import array

def homepage(request):
    groups = [ ]
    for gm in GroupUser.objects.filter(user=request.user):
        groups.append(gm.group)

    events = list(EventGroup.objects.filter(group__in=groups))

    return render_to_response('nourish/homepage.html', { 
        'request': request,
        'events' : events,
        'groups' : groups,
    } )

def homepage_chooser(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return redirect('/home')
    if profile.role == 'E':
        try:
            eu = EventUser.objects.get(user=user,admin=True)
        except EventUser.DoesNotExist:
            return redirect('/events/create')
        return HttpResponseRedirect(eu.event.get_absolute_url())
    if profile.role == 'T':
        gus = GroupUser.objects.filter(user=user,admin=True)
        if len(gus) > 1:
            return HttpResponseRedirect('/home')
        if not len(gus):
            return HttpResponseRedirect('/groups/create?host')
        egs = EventGroup.objects.filter(group=gus[0].group)
        if len(egs) == 1:
            return HttpResponseRedirect(egs[0].get_absolute_url())
        return redirect('/home')
    if profile.role == 'A':
        gus = GroupUser.objects.filter(user=user,admin=True)
        if len(gus) > 1:
            return redirect('/home')
        if not len(gus):
            return redirect('/groups/create?guest')
        egs = EventGroup.objects.filter(group=gus[0].group)
        if len(egs) == 1:
            return redirect(egs[0].get_absolute_url())
        return redirect('/home')
    return redirect('/home')
