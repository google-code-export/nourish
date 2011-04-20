from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from nourish.models import EventUser, Event, GroupUser, Group, EventGroup, UserProfile, User, Meal, MealInvite
from nourish.forms.meal import EventGroupInviteForm, EventGroupMealForm, EventGroupInvitesForm
from django.http import HttpResponseRedirect
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required

def event_group_invite(request, event_id, event_group_id, host_eg_id):
    eg = EventGroup.objects.get(id=event_group_id)
    host_eg = EventGroup.objects.get(id=host_eg_id)
    event = Event.objects.get(id=event_id)
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
            return HttpResponseRedirect(eg.get_absolute_url()) # Redirect after POST

    else:
        form = EventGroupInviteForm() # An unbound form

        ms = []
        for meal in meals:
            ms.append(meal.id)

        form.fields['meals'].queryset = meals

        form.initial = { 'meals' : ms }

    return render_to_response('nourish/meal/invite.html', {
        'form': form,
        'host_eg': host_eg,
        'eg': eg,
        'event' : event,
        'request': request,
    })

@login_required
def event_group_meals(request, event_id, event_group_id):
    eg = EventGroup.objects.get(id=event_group_id)
    event = Event.objects.get(id=event_id)
    meals = Meal.objects.filter(eg=eg)

    try:
        gu = GroupUser.objects.get(group=eg.group,user=request.user,admin=True)
    except GroupUser.DoesNotExist:
        raise PermissionDenied

    initial = []
    choices = []
    for meal in meals:
        i = { 
            'date': meal.date,
            'meal_id': meal.id,
            'members' : meal.members,
            'invite' : 'un',
        }
        c = []
        if (meal.state in ['N', 'I', 'S' ]):
            c.append(('un', 'Undecided'))
        for invite in MealInvite.objects.filter(meal=meal):
            if invite.state not in ['N', 'S', 'C']:
                continue
            group = invite.host_eg.group
            c.append((invite.id, group.name + ' (' + invite.host_eg.dinner_time + ', ' + invite.host_eg.features + ')'))
            if invite.state in [ 'S', 'C' ]:
                i['invite'] = invite.id
        initial.append(i)
        choices.append(c)

    MealFormSet = formset_factory(EventGroupMealForm,extra=0)
    if request.method == 'POST': # If the form has been submitted...
        formset = MealFormSet(request.POST)
        i = iter(choices)
        for form in formset:
            form.fields['invite'].choices = i.next()
        if formset.is_valid(): # All validation rules pass
            i = iter(choices)
            for data in formset.cleaned_data:
                meal = Meal.objects.get(id=data['meal_id'])
                if data['invite'] == 'un':
                    if meal.state == 'S':
                        meal.unchoose()
                else:
                    invite = MealInvite.objects.get(id = int(data['invite']))
                    if not meal.invite or meal.invite != invite:
                        meal.choose(invite)
                
            return HttpResponseRedirect(eg.get_absolute_url()) 
    else:
        formset = MealFormSet(initial=initial)
        i = iter(choices)
        for form in formset:
            form.fields['invite'].choices = i.next()

    return render_to_response('nourish/meal/event_group.html', {
        'formset': formset,
        'eg': eg,
        'event' : event,
        'request' : request,
    })

def event_group_invites(request, event_id, event_group_id):
    eg = EventGroup.objects.get(id=event_group_id)
    event = Event.objects.get(id=event_id)
    
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
            return HttpResponseRedirect(eg.get_absolute_url()) 

    else:
        formset = InvitesFormSet(initial=initial)

    forms = { 'N' : [ ], 'S' : [ ], 'C' : [ ], 'R' : [ ], }
    for form in formset:
        invite = invites[int(form['invite_id'].value())]
        forms[invite.state].append((form,invite))

    return render_to_response('nourish/meal/event_group_invites.html', {
        'formset': formset,
        'eg': eg,
        'event' : event,
        'request' : request,
        'invites' : invites,
        'forms' : forms,
    })
