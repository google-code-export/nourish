from django.shortcuts import render_to_response, redirect
from django.core.exceptions import PermissionDenied
from nourish.models import GroupUser, EventGroup, Meal, MealInvite
from nourish.forms.meal import EventGroupInviteForm, EventGroupMealForm, EventGroupInvitesForm
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required
from datetime import timedelta

def event_guest_invite(request, pk, host_eg_id):
    eg = EventGroup.objects.get(id=pk)
    host_eg = EventGroup.objects.get(id=host_eg_id)
    event = eg.event
    meals = Meal.objects.filter(eg=eg,state__in=['N','I','S'])
    if request.method == 'POST': # If the form has been submitted...
        form = EventGroupInviteForm(request.POST) # A form bound to the POST data
        form.fields['meals'].queryset = meals
        if form.is_valid(): # All validation rules pass
            data = form.cleaned_data
            for meal in meals:
                if meal in data['meals']:
                    try:
                        invite = MealInvite.objects.get(meal=meal,host_eg=host_eg)
                    except MealInvite.DoesNotExist:
                        meal.invite(host_eg)
                else:
                    try:
                        invite = MealInvite.objects.get(meal=meal,host_eg=host_eg)
                    except MealInvite.DoesNotExist:
                        continue
                    invite.rescind()
#
            return redirect(eg.get_absolute_url()) # Redirect after POST

    else:
        form = EventGroupInviteForm() # An unbound form

        ms = []
        for meal in meals:
            ms.append(meal.id)

        form.fields['meals'].queryset = meals

        form.initial = { 'meals' : ms }

    return render_to_response('nourish/event_guest_invite.html', {
        'form': form,
        'host_eg': host_eg,
        'eg': eg,
        'event' : event,
        'request': request,
    })

@login_required
def event_guest_meals(request, pk):
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
        print "key is " + k
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
                c.append(('un', 'Undecided'))
                if meals[k] in invites_by_meal:
                    for invite in invites_by_meal[meals[k]]:
                        c.append( ( invite.id, invite ) )
            else:
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
            for form in formset.cleaned_data:
                d = date.next()
                if form['meal_id']:
                    meal = Meal.objects.get(pk=form['meal_id'])
                    if form['members'] < 1:
                        meal.delete()
                        continue
                else:
                    if form['members'] > 0:
                        meal = eg.meal(d, 'D')
                    else:
                        continue

                meal.members = form['members']
                meal.features = ''.join(form['features'])
                meal.notes = ''.join(form['notes'])
                meal.save()

            return redirect(eg.get_absolute_url()) 
    else:
        formset = MealFormSet(initial=initial)
        i = iter(choices)
        for form in formset:
            form.fields['invite'].choices = i.next()

    return render_to_response('nourish/event_guest_meals.html', {
        'formset': formset,
        'eg': eg,
        'event' : event,
        'request' : request,
        'meals' : iter(display_info),
        'dates' : iter(dates),
        'days' : iter(dates),
    })

def event_host_invites(request, pk):
    eg = EventGroup.objects.get(id=pk)
    event = eg.event
    
    initial = [] 
    invites = { }
    for invite in MealInvite.objects.filter(host_eg=eg):
        action = False
        if invite.state == 'S':
            action = True
        initial.append({
            'invite_id' : invite.id,
            'action' : action
        })
        invites[invite.id] = invite

    InvitesFormSet = formset_factory(EventGroupInvitesForm,extra=0)
    if request.method == 'POST': # If the form has been submitted...
        formset = InvitesFormSet(request.POST)
        if formset.is_valid(): # All validation rules pass
            data = formset.cleaned_data
            for form in data:
                invite = invites[int(form['invite_id'])]
                if form['action']:
                    if invite.state == 'S':
                        invite.confirm()
                    else:
                        invite.rescind()
            return redirect(eg.get_absolute_url()) 

    else:
        formset = InvitesFormSet(initial=initial)

    forms = { 'N' : [ ], 'S' : [ ], 'C' : [ ], 'R' : [ ], }
    for form in formset:
        invite = invites[int(form['invite_id'].value())]
        forms[invite.state].append((form,invite))

    return render_to_response('nourish/event_host_invites.html', {
        'formset': formset,
        'eg': eg,
        'event' : event,
        'request' : request,
        'invites' : invites,
        'forms' : forms,
        'has_invites' : has_invites,
    })
