from django.views.generic import DetailView, UpdateView, ListView
from nourish.models import EventGroup, Event, GroupUser, Meal, MealInvite, EventUser
from nourish.forms import EventForm, EventGroupHostForm, EventInviteDayForm, EventInviteMealForm
from nourish.forms.event import EventGroupHostFeaturesForm, EventGroupHostForm
from nourish.forms.register import RegistrationStubForm
from nourish.forms.group import GroupForm, GroupFBForm
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta
from fbcanvas.views import HybridCanvasView
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'host' not in request.GET:
            raise Exception("no host_eg specified")
        host_eg = EventGroup.objects.get(id=request.GET['host'])
        if not request.user.is_authenticated() or not host_eg.group.is_admin(request.user):
            raise PermissionDenied
        guest_eg = None
        if 'guest' in request.GET:
            guest_eg = EventGroup.objects.get(id=request.GET['guest'])
    
        day_factory = formset_factory(EventInviteDayForm, extra=0)
        meal_factory = formset_factory(EventInviteMealForm, extra=0)

        day_formset = day_factory(request.POST, prefix='days')
        meal_formset = meal_factory(request.POST, prefix='meals')

        context = super(EventInviteView, self).get_context_data(object=self.object)

        (dates, day_initial, meal_initial) = self.get_meals(host_eg, guest_eg, 'manage' in self.request.GET)

        dates = self.get_dates(dates, day_formset, meal_formset)

        context['dates'] = dates
        context['day_formset'] = day_formset
        context['meal_formset'] = meal_formset
        context['host_eg'] = host_eg

        if (not meal_formset.is_valid()) or (not day_formset.is_valid()):
            context['error'] = True
            return self.render_to_response(context)

        day_data = day_formset.cleaned_data
        meal_data = meal_formset.cleaned_data

        dd = iter(day_data)
        md = iter(meal_data)
        
        missing = False;

        for day in dates:
            needed = False
            for meal in day['meals']:
                data = md.next()
                if data['invited']:
                    needed = True
            data = dd.next()
            if needed and not data['dinner_time']:
                day['form'].errors['dinner_time'] = ['You must specify a dinner time']
                missing = True

        if missing:
            context['error'] = True
            return self.render_to_response(context)

        dd = iter(day_data)
        md = iter(meal_data)

        to_invite = []
        to_confirm = []
        to_rescind = []
        to_change = []

        for day in dates:
            data = dd.next()
            dinner_time = data['dinner_time']
            for m in day['meals']:
                mdata = md.next()
                meal = Meal.objects.get(id = mdata['meal_id'])
#                if meal.state != 'N' and not meal.invite:
                    # drop bad invites 
                    # meal.state = 'N'
                    # meal.save()
                    # continue;
                if (meal.state == 'N'):
                    if 'invited' in mdata and mdata['invited']:
                        to_invite.append( (meal, dinner_time) )
                    continue
                elif (meal.state == 'I'):
                    if 'invited' not in mdata or not mdata['invited']:
                        to_rescind.append(MealInvite.objects.get(host_eg=host_eg,meal=meal))
                    continue
                elif (meal.state == 'S'):
                    if 'invited' in mdata and mdata['invited']:
                        to_confirm.append(meal.invite)
                        continue
                    else:
                        to_rescind.append(meal.invite)
                        continue
                elif (meal.state == 'C'):
                    if 'invited' not in mdata or not mdata['invited']:
                        to_rescind.append(meal.invite)
                        continue
                if str(meal.invite.dinner_time) != str(dinner_time):
                    sys.stderr.write("[%s] != [%s]\n" % (meal.invite.dinner_time, dinner_time) )
                    meal.invite.dinner_time = dinner_time
                    to_change.append(meal.invite)

        host_eg.rescind_invites(to_rescind)
        host_eg.confirm_invites(to_confirm)
        host_eg.send_invites(to_invite)
        host_eg.change_invites(to_change)

        return redirect(host_eg.get_absolute_url('canvas' in context))

    def get_context_data(self, **kwargs):
        host_eg = None
        if 'host' in self.request.GET:
            host_eg = EventGroup.objects.get(id=self.request.GET['host'])
        context = super(EventInviteView, self).get_context_data(**kwargs)

        guest_eg = None
        if 'guest' in self.request.GET:
            guest_eg = EventGroup.objects.get(id=self.request.GET['guest'])

        (dates, day_initial, meal_initial) = self.get_meals(host_eg, guest_eg, 'manage' in self.request.GET)

        day_factory = formset_factory(EventInviteDayForm, extra=0)
        meal_factory = formset_factory(EventInviteMealForm, extra=0)

        day_formset = day_factory(prefix='days', initial=day_initial)
        meal_formset = meal_factory(prefix='meals', initial=meal_initial)

        dates = self.get_dates(dates, day_formset, meal_formset)

        is_fb = False
        if self.request.user.is_authenticated() and self.request.user.get_profile().provider == 'F':
            is_fb = True
        if 'nofb' in self.request.GET:
            is_fb = False

        RegistrationFormset = formset_factory(RegistrationStubForm, extra=0)
        GroupHostFormset = formset_factory(EventGroupHostForm, extra=0)
        FeaturesFormset = formset_factory(EventGroupHostFeaturesForm, extra=0)
        if is_fb:
            GroupFormset = formset_factory(GroupFBForm, extra=0)
        else:
            GroupFormset = formset_factory(GroupForm, extra=0)

        user_formset = RegistrationFormset(prefix='user', initial=[{
            'role': 'A',
        }])
        grouphost_formset = GroupHostFormset(prefix='grouphost', initial=[{
            'dinner_time' : '6:00pm',
            'features' : [ 'd', 'p' ],
        }])
        group_formset = GroupFormset(prefix='group', initial=[{
            'role' : 'A',
        }])
        features_formset = FeaturesFormset(prefix='features', initial=[{}])
        if is_fb:
#            choices = get_group_choices(self.request.facebook.graph, self.object, self.request.user)
            choices = []
            group_formset[0].fields['group'].choices = choices
                
        context['dates'] = dates
        context['day_formset'] = day_formset
        context['meal_formset'] = meal_formset
        context['host_eg'] = host_eg

        context['user_formset'] = user_formset
        context['grouphost_formset'] = grouphost_formset
        context['group_formset'] = group_formset
        context['features_formset'] = features_formset

        context['is_fb'] = is_fb

        return context

    def get_meals(self, eg, guest_eg=None, manage=False):
        d = { }
        if guest_eg:
            meals = Meal.objects.filter(event=self.object,eg=guest_eg).order_by('date')
        else:
            meals = Meal.objects.filter(event=self.object).order_by('date')
        for meal in meals:
            if meal.state == 'S' or meal.state == 'C':
                if not meal.invite:
                    sys.stderr.write("no invite :(\n")
                    continue
            if meal.state == 'N':
                if manage:
                    continue
            else:
                invite = meal.invite
                if meal.state == 'I':
                    try:
                        invite = MealInvite.objects.get(host_eg=eg, meal=meal)
                    except MealInvite.DoesNotExist:
                        invite = None
                if not invite or invite.host_eg != eg:
                    sys.stderr.write("not mine\n")
                    continue
            if meal.date not in d:
                d[meal.date] = []
            d[meal.date].append(meal)

        day_initial = []
        meal_initial = []

        keys = d.keys()
        keys.sort()

        for date in keys:
            dinner_time = ''
            for meal in d[date]:
                meal_initial.append({ 'meal_id' : meal.id, 'invited' : (meal.state != 'N') })
                if not dinner_time:
                    if meal.invite:
                        dinner_time = meal.invite.dinner_time
                    else:
                        try:    
                            invite = MealInvite.objects.get(host_eg=eg,meal=meal)
                            dinner_time = invite.dinner_time
                        except MealInvite.DoesNotExist:
                            pass
            day_initial.append({ 'date' : date, 'dinner_time' : dinner_time })

        return (d, day_initial, meal_initial)

    def get_dates(self, dates, day_formset, meal_formset):
        df = iter(day_formset)
        mf = iter(meal_formset)

        keys = dates.keys()
        keys.sort()
        out = []
        for date in keys:
            meals = []
            for meal in dates[date]:
                meals.append({ 'meal' : meal, 'form' : mf.next() })
            out.append({ 'date' : date, 'form' : df.next(), 'meals' : meals })

        return out
