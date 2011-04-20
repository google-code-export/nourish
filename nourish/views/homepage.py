from django.shortcuts import render_to_response
from nourish.models import EventUser, Event, GroupUser, Group, EventGroup
import array

def homepage(request):

        groups = [ ]
        for gm in GroupUser.objects.filter(user=request.user):
            groups.append(gm.group)

        events = list(EventGroup.objects.filter(group__in=groups))
#        events.sort(key=lambda event: .event['date'])

        return render_to_response('nourish/homepage.html', { 
            'request': request,
            'events' : events,
            'groups' : groups,
        } )
