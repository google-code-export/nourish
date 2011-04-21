from django.views.generic import DetailView
from nourish.models import EventGroup, Event, GroupUser, Meal, MealInvite
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta

class EventDetailView(DetailView):
    context_object_name = 'event'
    model = Event
    template_name='nourish/event_detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['host_list'] = []
        context['guest_list'] = []
        for eg in EventGroup.objects.filter(event=self.object):
            if eg.group.role == 'T':
                context['host_list'].append(eg)
            if eg.group.role == 'A':
                context['guest_list'].append(eg)
        return context

class EventGroupView(DetailView):
    context_object_name = 'event_group'
    model = EventGroup
    template_name='nourish/event_group.html'
    
    def get_context_data(self, **kwargs):
        context = super(EventGroupView, self).get_context_data(**kwargs)
        context['meals'] = Meal.objects.filter(eg=self.object).order_by('date', 'meal')
        context['invites_sent'] = MealInvite.objects.filter(host_eg=self.object)
        context['invites_rcvd'] = MealInvite.objects.filter(guest_eg=self.object)
        dates = []
        date = self.object.event.start_date
        while date <= self.object.event.end_date:
            dates.append(date)
            date += timedelta(days=1)
        context['dates'] = dates
        groups = []
        group_admin = True;
        if self.request.user.is_authenticated():
            for g in GroupUser.objects.filter(user=self.request.user,admin=True):
                groups.append(g.group.id)
            try:
                gu = GroupUser.objects.get(group=self.object.group,user=self.request.user,admin=True)
            except GroupUser.DoesNotExist:
                group_admin = False
        else:
            group_admin = False
        
        host_egs = EventGroup.objects.filter(role='T', group__in=groups)
        context['host_event_groups'] = host_egs
        context['group_admin'] = group_admin
        return context
