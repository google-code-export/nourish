from django.shortcuts import render_to_response
from nourish.models import EventUser, Event, GroupUser, Group, EventGroup, UserProfile, User, Meal
from nourish.forms.register import RegistrationStubForm, EventRegistrationForm
from nourish.forms.group import GroupStubForm
from nourish.forms.meal import MealStubForm
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate
from datetime import timedelta
from django.forms.formsets import formset_factory
import array
from django import forms

def register(request):
    if request.method == 'POST': # If the form has been submitted...
        form = RegistrationStubForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            data = form.cleaned_data
            user = User.objects.create_user(data['username'], data['email'], data['password'])
            authuser = authenticate(username=data['username'], password=data['password'])
            login(request,authuser)
            profile = UserProfile.objects.create(
                user=user,
                role=data['role'],
                url=data['url'],
            )
            return HttpResponseRedirect('/logged-in/') # Redirect after POST
    else:
        form = RegistrationStubForm() # An unbound form

    return render_to_response('nourish/register.html', {
        'form': form,
    })

def event_register_guest(request, event_id):
    event = Event.objects.get(id=event_id)
    initial = []
    dates = []
    date = event.start_date
    while date <= event.end_date:
        initial.append({
            'date' : date,
            'meal' : 'D',
            'event' : event,
            'eg' : None,
            'state' : 'N',
        })
        dates.append(date)
        date += timedelta(days=1)
#    feature_choices = [ ('R', 'Yes' ) ]
    RegistrationFormset = formset_factory(RegistrationStubForm, extra=0)
    GroupFormset = formset_factory(GroupStubForm, extra=0)
    MealFormset = formset_factory(MealStubForm, extra=0)
    if request.method == 'POST':
        user_formset = RegistrationFormset(request.POST, prefix='user')
        group_formset = GroupFormset(request.POST, prefix='group')
        meal_formset = MealFormset(request.POST, prefix='meal')
#        for form in meal_formset:
#            form.fields['features'].choices = feature_choices
    else:
        user_formset = RegistrationFormset(prefix='user', initial=[{
            'role' : 'A',
        }])
        group_formset = GroupFormset(prefix='group', initial=[{
            'role' : 'A',
        }])
        meal_formset = MealFormset(prefix='meal', initial=initial)
#        for form in meal_formset:
#            form.fields['features'].choices = feature_choices

    return render_to_response('nourish/event_register_guest.html', {
        'request' : request,
        'user_formset' : user_formset,
        'group_formset' : group_formset,
        'meal_formset' : meal_formset,
        'event': event,
        'dates': iter(dates),
        'days': iter(dates),
    })

def event_register(request, pk, role):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST': # If the form has been submitted...
        form = EventRegistrationForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            data = form.cleaned_data

            user = User.objects.create_user(
                data['username'], 
                data['email'], 
                data['password']
            )

            authuser = authenticate(
                username=data['username'], 
                password=data['password']
            )
            login(request, authuser)

            if (role == 'guest'):
                members         = int(data['members'])
                notes           = str(data['notes'])
                dinner_time     = 0
            else:
                dinner_time     = str(data['dinner_time'])
                members         = 0
                notes           = ''

            features            = ''.join(data['features'])

            profile = UserProfile.objects.create(
                user            = user,
                role            = data['role'],
            )
            group = Group.objects.create(
                name            = data['group_name'],
                url             = data['group_url'],
                role            = data['role'],
                members         = members,
            )

            gu = group.user(user)
            gu.admin            = True
            gu.save()

            eg = event.group(group)
            eg.arrival_date     = data['arrival_date']
            eg.departure_date   = data['departure_date']
            eg.dinner_time      = dinner_time
            eg.expected_members = members
            eg.role             = data['role']
            eg.features         = features
            eg.notes            = notes,
            eg.save()

            eu = event.user(user)
            eu.group            = group
            eu.arrival_date     = data['arrival_date']
            eu.departure_date   = data['departure_date']
            eu.save()

            
            if data['role'] == 'A':
                date = data['arrival_date']
                while date <= data['departure_date']:
                    meal = eg.meal(date,'D')
                    date += timedelta(days=1)
        
            return HttpResponseRedirect('/logged-in/') # Redirect after POST
    else:
        if role == 'guest':
            dbrole = 'A'
        if role == 'host':
            dbrole = 'T'

        initial = {
            'event': pk,
            'role': dbrole,
            'arrival_date': event.start_date,
            'departure_date': event.end_date,
            'members' : 1
        }

        form = EventRegistrationForm(initial=initial) # An unbound form

    return render_to_response('nourish/event_register.html', {
        'form': form,
        'event': event,
        'role': role,
    })

def login_redir(request):
    user = request.user
    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        return HttpResponseRedirect('/home')
    if profile.role == 'E':
        try:
            eu = EventUser.objects.get(user=user,admin=True)
        except EventUser.DoesNotExist:
            return HttpResponseRedirect('/events/create')
        return HttpResponseRedirect(eu.event.get_absolute_url())
    if profile.role == 'T':
        gus = GroupUser.objects.filter(user=user,admin=True)
        if len(gus) > 1:
            return HttpResponseRedirect('/home')
        if not len(gus):
            return HttpResponseRedirect('/groups/create?host')
        egs = EventGroup.objects.filter(group=gus[0].group,attending='Y')
        if len(egs) == 1:
            return HttpResponseRedirect(egs[0].get_absolute_url())
        return HttpResponseRedirect('/home')
    if profile.role == 'A':
        gus = GroupUser.objects.filter(user=user,admin=True)
        if len(gus) > 1:
            return HttpResponseRedirect('/home')
        if not len(gus):
            return HttpResponseRedirect('/groups/create?guest')
        egs = EventGroup.objects.filter(group=gus[0].group,attending='Y')
        if len(egs) == 1:
            return HttpResponseRedirect(egs[0].get_absolute_url())
        return HttpResponseRedirect('/home')
    return HttpResponseRedirect('/home')
