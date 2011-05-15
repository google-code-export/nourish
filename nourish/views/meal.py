from django.shortcuts import render_to_response, redirect
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from nourish.models import GroupUser, EventGroup, Meal, MealInvite
from nourish.forms.meal import EventGroupInviteForm, EventGroupMealForm, EventGroupInvitesForm
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from datetime import timedelta
import sys
from pprint import pformat

@login_required
def event_guest_meals(request, pk, canvas=False):
    eg = EventGroup.objects.get(id=pk)
    event = eg.event

    try:
        gu = GroupUser.objects.get(group=eg.group,user=request.user,admin=True)
    except GroupUser.DoesNotExist:
        raise PermissionDenied

    dates = []
    date = event.start_date
    while date <= event.end_date:
        dates.append(date)
        date += timedelta(days=1)

    show_meals = [ ('D', 'Dinner') ]

    meals = Meal.objects.filter(eg=eg)
    invites = MealInvite.objects.filter(guest_eg=eg)

    m = {}
    for meal in meals:
        k = str(meal.date) + ':' + meal.meal
        m[k] = meal
    meals = m


    invites_by_meal = {}
    for invite in invites:
        if invite.meal not in invites_by_meal:
            invites_by_meal[invite.meal] = []
        invites_by_meal[invite.meal].append(invite)
    
    initial = []
    choices = []
    display_info = []
    has_invites = []
    mealset = []
    for date in dates:
        for sm in show_meals:
            display_info.append(sm[1])
            k = str(date) + ':' + sm[0]
            i = { 'date' : date, 'meal' : sm[0] }
            c = [ ]
            if k in meals:
                has_invites.append(True)
                i['meal_id'] = meals[k].id
                i['meal'] = meals[k].meal
                i['members'] = meals[k].members
                i['features'] = meals[k].features
                i['notes'] = meals[k].notes
                if meals[k].invite:
                    i['invite'] = str(meals[k].invite.id)
                else:
                    i['invite'] = 'un'
                meal = Meal.objects.get(id=meals[k].id)
                if meal.state in [ 'I', 'S' ]:
                    c.append(('un', 'Select an Invitation!'))
                    if meals[k] in invites_by_meal:
                        for invite in invites_by_meal[meals[k]]:
                            c.append( ( invite.id, invite.host_eg.group.name ) )
                mealset.append(meals[k])
            else:
                mealset.append(None)
                has_invites.append(False)
            choices.append(c)
            initial.append(i)

    MealFormSet = formset_factory(EventGroupMealForm,extra=0)
    if request.method == 'POST':
        formset = MealFormSet(request.POST)
        i = iter(choices)
        for form in formset:
            form.fields['invite'].choices = i.next()
        date = iter(dates)
        if formset.is_valid():
            to_choose = []
            to_unchoose = []
            to_delete = []
            to_add = []
            to_change = []
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
                        meal = eg.meal(d, 'D')
                        meal.members = form['members']
                        meal.features = ''.join(form['features'])
                        meal.notes = ''.join(form['notes'])
                        to_add.append(meal)
                        continue

    
            eg.delete_meals(to_delete)
            eg.unchoose_meals(to_unchoose)
            eg.change_meals(to_change)
            eg.choose_invites(to_choose)
            eg.add_meals(to_add)

            return redirect(eg.get_absolute_url(canvas)) 
    else:
        formset = MealFormSet(initial=initial)
        i = iter(choices)
        for form in formset:
            form.fields['invite'].choices = i.next()

    forms_and_meals = []
    meals = iter(mealset)
    for form in formset:
        forms_and_meals.append((form, meals.next()))

    return render_to_response('nourish/event_guest_meals.html', {
        'formset': formset,
        'eg': eg,
        'event' : event,
        'request' : request,
        'meals' : iter(display_info),
        'dates' : iter(dates),
        'days' : iter(dates),
        'f_m' : forms_and_meals,
        'canvas' : canvas
    }, context_instance=RequestContext(request))
