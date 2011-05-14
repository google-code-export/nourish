from django.views.generic import DetailView, UpdateView, ListView
from nourish.models import EventGroup, Event, GroupUser, Meal, MealInvite, EventUser
from nourish.forms import EventForm, EventGroupHostForm, EventInviteDayForm, EventInviteMealForm
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta
from nourish.views.canvas import HybridCanvasView
from django.forms.formsets import formset_factory
import json

import sys
from pprint import pformat
import pprint

class EventDetailView(HybridCanvasView, DetailView):
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

class EventGroupView(HybridCanvasView, DetailView):
    context_object_name = 'event_group'
    model = EventGroup
    template_name='nourish/event_group.html'
    
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
    template_name='nourish/event_list.html',
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


class EventInviteView(HybridCanvasView, DetailView):
    context_object_name = 'event_invite'
    model = Event
    template_name = 'nourish/event_invite.html'
    def get_context_data(self, **kwargs):
        eg = None
        if 'eg' in self.request.GET:
            eg = EventGroup.objects.get(id=self.request.GET['eg'])
        context = super(EventInviteView, self).get_context_data(**kwargs)
        d = { }
        meals = Meal.objects.filter(event=self.object).order_by('date')
        for meal in meals:
            if meal.state != 'I':
                if meal.invite and meal.invite.host_eg != eg:
                    continue
            if meal.date not in d:
                d[meal.date] = []
            d[meal.date].append(meal)
        dates = []
        keys = d.keys()
        keys.sort()
        raw = []
        day_factory = formset_factory(EventInviteDayForm, extra=0)
        meal_factory = formset_factory(EventInviteMealForm, extra=0)
        day_initial = []
        for date in keys:
            d[date].sort()
            rec = { 'date' : date.strftime("%b %d"), 'dinner_time' : '', 'meals' : [ ] }
            day_initial.append({ 'date' : date, 'dinner_time' : '' })
            meal_initial = []
            meals = []
            for meal in d[date]:
                meals.append(meal)
                rec['meals'].append({
                    'id' : meal.id,
                    'guest_name' : meal.eg.group.name,
                    'guest_url' : meal.eg.group.url,
                    'guest_image_url' : meal.eg.group.image_url,
                    'diners' : meal.members,
                    'features' : meal.features,
                    'state' : meal.state,
                    'notes' : meal.notes,
                })
                meal_initial.append({ 'meal_id' : meal.id, 'invited' : (meal.state == 'I') })
            raw.append(rec)
            meal_formset = meal_factory(prefix='d' + date.strftime("%Y%m%d"), initial=meal_initial)
            m = iter(meals)
            f = iter(meal_formset)
            mealsets = []
            while True:
                try:
                    mealsets.append( (m.next(), f.next()) )
                except:
                    break
            dates.append( { 
                'date' : date, 
                'meals' : meals,
                'formset' : meal_formset,
                'mealsets' : mealsets,
            } )
        daysets = []
        day_formset = day_factory(prefix='days', initial=day_initial)
        f = iter(day_formset)
        for d in dates:
            daysets.append({
                'date' : d['date'],
                'form' : f.next(),
                'mealsets' : d['mealsets'],
            })
        context['daysets'] = daysets
        context['day_formset'] = day_formset
        context['dates'] = dates
        context['json'] = json.dumps(raw)
        return context
