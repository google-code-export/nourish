from django.shortcuts import render_to_response
from nourish.models import EventUser, Event, GroupUser, Group, EventGroup
import array

def homepage(request):
	event_ids = [ ]
	for eu in EventUser.objects.filter(user=request.user):
		event_ids.append(eu.event.id)
	events = Event.objects.filter(pk__in=event_ids)

	group_ids = [ ]
	for gm in GroupUser.objects.filter(user=request.user):
		group_ids.append(gm.group.id);
	groups = Group.objects.filter(pk__in=group_ids);

	events_att = [ ]
	for ge in EventGroup.objects.filter(group__id__in=group_ids):
		events.append(Event.objects.get(pk=ge.event.id));
	
	return render_to_response('nourish/homepage.html', { 
		'request': request,
		'events' : events,
		'groups' : groups,
	} )
