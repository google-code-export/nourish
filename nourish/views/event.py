from django.views.generic import DetailView, UpdateView, ListView
from nourish.models import EventGroup, Event, GroupUser, Meal, MealInvite, EventUser
from nourish.forms import EventForm, EventGroupHostForm, EventInviteDayForm, EventInviteMealForm
from nourish.forms.event import EventGroupHostFeaturesForm, EventGroupHostForm
from nourish.forms.register import RegistrationStubForm
from nourish.forms.group import GroupForm, GroupFBForm
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta
from fbcanvas.views import HybridCanvasView
from nourish.views.register.host import EventHostRegisterView
from django.forms.formsets import formset_factory
import json

import sys
from pprint import pformat
import pprint

class EventDetailView(HybridCanvasView, DetailView):
    context_object_name = 'event'
    model = Event
    template_name='nourish/EventDetailView.html'

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

class EventSummaryView(HybridCanvasView, DetailView):
    context_object_name = 'event'
    model = Event
    template_name='nourish/EventSummaryView.html'

    def get_context_data(self, **kwargs):
        dates = { }
        totals = { 
            'tot_meals' : 0,
            'new_meals' : 0,
            'inv_meals' : 0,
            'con_meals' : 0,
            'tot_crew'  : 0,
            'new_crew'  : 0,
            'inv_crew'  : 0,
            'con_crew'  : 0,
        }
        context = super(EventSummaryView, self).get_context_data(**kwargs)
        for meal in Meal.objects.filter(event=self.object):
            if meal.date not in dates:
                dates[meal.date] = { 
                    'date' : meal.date,
                    'tot_meals' : 0,
                    'new_meals' : 0,
                    'inv_meals' : 0,
                    'con_meals' : 0,
                    'tot_crew'  : 0,
                    'new_crew'  : 0,
                    'inv_crew'  : 0,
                    'con_crew'  : 0,
                }
            totals['tot_meals'] += 1
            totals['tot_crew'] += meal.members
            dates[meal.date]['tot_meals'] += 1
            dates[meal.date]['tot_crew'] += meal.members
            if meal.state == 'I':
                dates[meal.date]['inv_meals'] += 1
                dates[meal.date]['inv_crew'] += meal.members
                totals['inv_meals'] += 1
                totals['inv_crew'] += meal.members
            elif meal.state == 'C':
                dates[meal.date]['inv_meals'] += 1
                dates[meal.date]['inv_crew'] += meal.members
                totals['inv_meals'] += 1
                totals['inv_crew'] += meal.members
                dates[meal.date]['con_meals'] += 1
                dates[meal.date]['con_crew'] += meal.members
                totals['con_meals'] += 1
                totals['con_crew'] += meal.members

        date_list = [] 

        sys.stderr.write(pprint.pformat(dates))
        i = dates.keys()
        i.sort()
        for j in i:
            date_list.append(dates[j])

        context['mealdates'] = date_list
        context['mealtotals'] = totals

        return context

class EventGroupView(HybridCanvasView, DetailView):
    context_object_name = 'event_group'
    model = EventGroup
    template_name='nourish/EventGroupView.html'
    
    def get_context_data(self, **kwargs):
        context = super(EventGroupView, self).get_context_data(**kwargs)
        context['meals'] = Meal.objects.filter(eg=self.object).order_by('date', 'meal')
        context['invites_sent'] = MealInvite.objects.filter(host_eg=self.object)
        context['invites_rcvd'] = MealInvite.objects.filter(guest_eg=self.object)
        context['is_group_admin'] = self.object.group.is_admin(self.request.user)
        context['is_event_admin'] = self.object.event.is_admin(self.request.user)
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

class EventUpdateView(HybridCanvasView, UpdateView):
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

class EventListView(HybridCanvasView, ListView):
    template_name='nourish/EventListView.html'
    queryset=Event.objects.filter(display=True)
    
class EventGroupUpdateView(HybridCanvasView, UpdateView):
    context_object_name = 'eventgroup'
    model = EventGroup
    form_class = EventGroupHostForm
    login_required = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not self.get_object().group.is_admin(self.request.user):
            raise PermissionDenied
        return super(EventGroupUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not self.get_object().group.is_admin(self.request.user):
            raise PermissionDenied
        return super(EventGroupUpdateView, self).post(request, *args, **kwargs)
