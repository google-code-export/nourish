from django.shortcuts import render_to_response, redirect
from django.core.exceptions import PermissionDenied
from nourish.models import EventGroup, Meal, MealInvite, Event, EventUser
from nourish.forms.meal import EventGroupMealForm
from django.forms.formsets import formset_factory
from datetime import timedelta
from fbcanvas.views import HybridCanvasView
from django.views.generic import DetailView, TemplateView

from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

class EventArtistChart(HybridCanvasView, DetailView):
    template_name='nourish/artistchart.html'
    context_object_name = 'event'
    model = Event
    
    def get_context_data(self, **kwargs):
        context = super(EventArtistChart, self).get_context_data(**kwargs)

        meals = Meal.objects.filter(event=self.object)

        context['meals'] = meals

        return context
                
    def get_dates(self):
        dates = []
        date = self.object.event.start_date
        while date <= self.object.event.end_date:
            dates.append(date)
            date += timedelta(days=1)
        return dates

class EventReports(HybridCanvasView, DetailView):
    template_name='nourish/reports.html'
    context_object_name = 'event'
    model = Event

    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(EventReports, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventReports, self).get_context_data(**kwargs)

        context['host_list'] = []
        context['guest_list'] = []
        context['eventuser_list'] = EventUser.objects.filter(event=self.object,admin=True)
        for eg in EventGroup.objects.filter(event=self.object):
            if eg.group.role == 'T':
                context['host_list'].append(eg)
            if eg.group.role == 'A':
                context['guest_list'].append(eg)

        unconfirmed_guests = {}

        for invite in MealInvite.objects.filter(event=self.object):
            if invite.state != 'C':
                unconfirmed_guests[invite.guest_eg] = 1

        context['unconfirmed_guests'] = unconfirmed_guests

        meals = Meal.objects.filter(event=self.object)
        context['meals'] = meals

        return context

class EventGuestManageView(HybridCanvasView, DetailView):
    template_name = "nourish/EventGuestManageView.html"
    context_object_name = 'eg'
    model = EventGroup

    def get_context_data(self, **kwargs):
        context = super(EventGuestManageView, self).get_context_data(**kwargs)

        (meals_by_date, invites_by_meal) = self.meals_info()

        initial = []
        for date in self.get_dates():
            if date in meals_by_date:
                meal = meals_by_date[date]
                if meal.invite:
                    invite = str(meal.invite.id)
                else:
                    invite = 'un'
                initial.append({
                    'meal_id' : meal.id,
                    'members' : meal.members,
                    'features' : meal.features,
                    'notes' : meal.notes,
                    'invite' : invite,
                })
            else:
                initial.append({})

        MealFormSet = formset_factory(EventGroupMealForm,extra=0)
        meal_formset = MealFormSet(initial=initial)

        forms = self.forms_by_date(meal_formset, meals_by_date, invites_by_meal)

        context['meal_formset'] = meal_formset
        context['forms_by_date'] = forms

        return context

    def forms_by_date(self, formset, meals_by_date, invites_by_meal):
        f = iter(formset)

        forms = []

        for date in self.get_dates():
            form = f.next()
            if date in meals_by_date:
                meal = meals_by_date[date]
            else:
                meal = None
            if meal in invites_by_meal:
                choices = [ ('un', 'Choose an Invite') ]
                for invite in invites_by_meal[meal]:
                    choices.append( (invite.id, invite.host_eg.group.name) )
                form.fields['invite'].choices = choices
            forms.append({'form' : form, 'date' : date, 'meal' : meal })

        return forms

    def get_dates(self):
        dates = []
        date = self.object.event.start_date
        while date <= self.object.event.end_date:
            dates.append(date)
            date += timedelta(days=1)
        return dates

    def meals_info(self):
        meals = Meal.objects.filter(eg=self.object)
        invites = MealInvite.objects.filter(guest_eg=self.object)

        invites_by_meal = {}
        for invite in invites:
            if invite.meal not in invites_by_meal:
                invites_by_meal[invite.meal] = []
            invites_by_meal[invite.meal].append(invite)

        meals_by_date = {}
        for meal in meals:
            meals_by_date[meal.date] = meal

        return (meals_by_date, invites_by_meal)

    def post(self, request, *args, **kwargs):
        super(EventGuestManageView, self).post(request, *args, **kwargs)
        self.object = self.get_object()

        MealFormSet = formset_factory(EventGroupMealForm,extra=0)
        formset = MealFormSet(request.POST)
        (meals_by_date, invites_by_meal) = self.meals_info()
        forms = self.forms_by_date(formset, meals_by_date, invites_by_meal)

        if not formset.is_valid():
            return self.render_to_response({
                'eg' : self.object,
                'meal_formset' : formset,
                'forms_by_date' : forms,
            })

        to_choose = []
        to_unchoose = []
        to_delete = []
        to_add = []
        to_change = []

        date = iter(self.get_dates())

        for form in formset.cleaned_data:
            d = date.next()
            if form['meal_id']:
                # existing meal
                meal = Meal.objects.get(pk=form['meal_id'])
                if form['members'] < 1:
                    # got deleted
                    to_delete.append(meal)
                    continue
                if form['invite']:
                    if form['invite'] == 'un':
                        if meal.invite:
                            to_unchoose.append(meal)
                    else:
                        invite = MealInvite.objects.get(id=form['invite'])
                        if meal.invite != invite:
                            to_choose.append(invite)
                if meal.members != form['members'] or meal.features != ''.join(form['features']) or meal.notes != ''.join(form['notes']):
                    to_change.append( (meal, form) )
            else:
                if form['members'] > 0:
                    meal = self.object.meal(d, 'D')
                    meal.members = form['members']
                    meal.features = ''.join(form['features'])
                    meal.notes = ''.join(form['notes'])
                    to_add.append(meal)
                    continue


        self.object.delete_meals(to_delete)
        self.object.unchoose_meals(to_unchoose)
        self.object.change_meals(to_change)
        self.object.choose_invites(to_choose)
        self.object.add_meals(to_add)

        return redirect(self.object.get_absolute_url(hasattr(request, 'fbcanvas') and request.fbcanvas))

class ConfirmInviteView(HybridCanvasView, TemplateView):
    context_object_name = 'siteinvite'
    template_name='nourish/NotificationListView.html'

    def post(self, request, *args, **kwargs):
        next_url = '/nourish/home'
        if 'next' in request.POST:
            next_url = request.POST['next']

        if 'invite_id' not in request.POST:
            raise Exception("no invite specified")

        invite = MealInvite.objects.get(id=request.POST['invite_id'])

        if invite.guest_eg.group.is_admin(request.user):
            invite.guest_eg.choose_invites([ invite ])
        elif invite.host_eg.group.is_admin(request.user):
            invite.host_eg.confirm_invites([ invite ])
        else:
            raise PermissionDenied

        return redirect(next_url)

    def get(self, request, *args, **kwargs):
        raise Exception("this page is post-only")
