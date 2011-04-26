from django.views.generic import DetailView, UpdateView
from nourish.models import EventGroup, Event, GroupUser, Meal, MealInvite, EventUser
from nourish.forms import EventForm
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
        context['is_admin'] = self.object.is_admin(self.request.user)
        context['eventuser_list'] = EventUser.objects.filter(event=self.object,admin=True)
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
        context['is_group_admin'] = self.object.group.is_admin(self.request.user)
        dates = []
        date = self.object.event.start_date
        while date <= self.object.event.end_date:
            dates.append(date)
            date += timedelta(days=1)
        context['dates'] = dates
        groups = []
        group_admin = True;
        if self.request.user.is_authenticated():
            context['is_admin'] = self.object.group.is_admin(self.request.user)
            for g in GroupUser.objects.filter(user=self.request.user,admin=True):
                if g.group.role == 'T':
                    groups.append(g.group)
            host_egs = EventGroup.objects.filter(group__in=groups,event=self.object.event)
        else:
            context['is_admin'] = False
            host_egs = []
        
#        host_egs = EventGroup.objects.filter(role='T', group__in=groups)
        context['host_event_groups'] = host_egs
        return context

class EventUpdateView(UpdateView):
    context_object_name = 'event'
    model = Event
    form_class = EventForm
    login_required = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not self.get_object().is_admin(self.request.user):
            raise PermissionDenied
        return super(EventUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not self.get_object().is_admin(self.request.user):
            raise PermissionDenied
        return super(EventUpdateView, self).post(request, *args, **kwargs)
