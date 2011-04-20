from django.views.generic import DetailView, CreateView, UpdateView
from nourish.models import EventGroup, EventUser, Event
from nourish.forms.event import EventAttendForm
from nourish.models import EventUser, Event, EventGroup
from nourish.models import GroupUser, Group
from nourish.models import Meal, MealInvite
from django.shortcuts import get_object_or_404, redirect
from datetime import timedelta

class EventAttendView(DetailView):
    context_object_name = 'eventattend'
    form_class = EventAttendForm
    model = Event
    template_name = 'nourish/event/attend.html'

    def get_context_data(self, **kwargs):
        context = super(EventAttendView, self).get_context_data(**kwargs)
        try:
            a = EventUser.objects.get(event=self.object, user=self.request.user)
        except EventUser.DoesNotExist:
            a = EventUser(
                event=self.object,
                user=self.request.user,
                arrival_date=self.object.start_date,
                departure_date=self.object.end_date,
                arrival_meal='B',
                departure_meal='D',
                attending='N',
            )
        member_groups = list()
        event_admin_groups = list()
        groups = set()
        
        for gu in GroupUser.objects.filter(user=self.request.user,admin=True):
            try:
                eg = EventGroup.objects.get(event=self.object,group=gu.group)
            except EventGroup.DoesNotExist:
                eg = EventGroup(
                    event=self.object,
                    group=gu.group,
                    arrival_date=self.object.start_date,
                    departure_date=self.object.end_date,
                )
            event_admin_groups.extend([eg])
            member_groups.extend([gu.group])
        for ge in EventGroup.objects.filter(event=self.object):
                groups.add(ge.pk)
        for gu in GroupUser.objects.filter(user=self.request.user):
                if gu.group.pk in groups:
                        member_groups.extend([gu.group])
        
        context['form'] = EventAttendForm(instance=a)
        context['attend'] = a
        context['event_admin_groups'] = event_admin_groups
        context['member_groups'] = member_groups

        return context

    def post(self,request,pk=None):
        if 'confirm' not in request.POST:
            return self.get(request,pk=pk)

        event = get_object_or_404(Event, pk=pk)
        eu = event.user(self.request.user)

        try:
            group = Group.objects.get(pk=request.POST['group'])
        except Group.DoesNotExist:
            group = None
        except ValueError:
            group = None

        eu.group = group
        eu.save()

        if group:
            user_eg = event.group(group)
            user_eg.arrival_date = a.arrival_date
            user_eg.departure_date = a.departure_date
            user_eg.save()

        for gu in GroupUser.objects.filter(user=self.request.user,admin=True):
            if gu.group == user_e.group:
                continue
            eg = event.group(gu.group)
            eg.arrival_date = a.arrival_date
            eg.departure_date = a.departure_date
            k = 'group_' + str(gu.group.pk)
            if eg.pk is None:
                if k in request.POST:
                    eg.attending = 'Y'
            else:
                if k in request.POST:
                    eg.attending = 'Y'
                else:
                    eg.attending = 'N'
            eg.save()

        return redirect(event)

class EventDetailView(DetailView):
    context_object_name = 'event'
    model = Event
    template_name='nourish/event/detail.html'

    def get_context_data(self, **kwargs):
        context = super(EventDetailView, self).get_context_data(**kwargs)
        context['host_list'] = EventGroup.objects.filter(event=self.object,attending='Y',role='T')
        context['guest_list'] = EventGroup.objects.filter(event=self.object,attending='Y',role='A')
        if self.request.user.is_authenticated():
            try:
                context['attend'] = EventUser.objects.get(event=self.object,user=self.request.user)
            except EventUser.DoesNotExist:
                context['attend'] = None
        else:
            context['attend'] = None
        return context

class EventGroupView(DetailView):
    context_object_name = 'event_group'
    model = EventGroup
    template_name='nourish/event/group.html'
    
    def get_context_data(self, **kwargs):
        context = super(EventGroupView, self).get_context_data(**kwargs)
        context['meals'] = Meal.objects.filter(eg=self.object)
        context['invites_sent'] = MealInvite.objects.filter(host_eg=self.object)
        context['invites_rcvd'] = MealInvite.objects.filter(guest_eg=self.object)
        dates = []
        date = self.object.arrival_date
        while date <= self.object.departure_date:
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
