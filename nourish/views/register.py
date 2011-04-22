from django.template import RequestContext

from django.shortcuts import render_to_response, redirect
from nourish.models import Event, Group, UserProfile, User
from nourish.forms.register import RegistrationKeyStubForm, RegistrationStubForm
from nourish.forms.group import GroupStubForm
from nourish.forms.meal import MealStubForm
from nourish.forms.event import EventForm
from django.contrib.auth import login, authenticate
from datetime import timedelta
from django.forms.formsets import formset_factory
import array

def register_event(request):
    RegistrationFormset = formset_factory(RegistrationKeyStubForm, extra=0)
    EventFormset = formset_factory(EventForm, extra=0)
    if request.method == 'POST':
        user_formset = RegistrationFormset(request.POST, prefix='user')
        event_formset = EventFormset(request.POST, prefix='event')
        valid = False
        if event_formset.is_valid():
            if request.user.is_authenticated() or user_formset.is_valid():
                valid = True
        if valid:
            event_data = event_formset.cleaned_data[0];

            if request.user.is_authenticated():
                user = request.user
                profile = user.get_profile()
            else:
                user_data = user_formset.cleaned_data[0];
                user = User.objects.create_user(
                    user_data['username'], 
                    user_data['email'], 
                    user_data['password']
                )
                authuser = authenticate(
                    username=user_data['username'], 
                    password=user_data['password']
                )
                login(request, authuser)
                profile = UserProfile.objects.create(
                    user            = user,
                    role            = 'E',
                )

            if profile.role == 'U' or not profile.role:
                profile.role = 'E'
                profile.save()

            event = Event.objects.create(
                name = event_data['name'],
                start_date = event_data['start_date'],
                end_date = event_data['end_date'],
                url = event_data['url'],
            )

            eu = event.user(user)
            eu.admin = True;
            eu.save()

            return redirect('/logged-in/') 

    else:
        user_formset = RegistrationFormset(prefix='user', initial=[{
            'role' : 'E',
        }])
        event_formset = EventFormset(prefix='event', initial=[{ }])

    return render_to_response('nourish/register_event.html', {
        'request' : request,
        'user_formset' : user_formset,
        'event_formset' : event_formset,
        'next' : request.get_full_path(),
    }, context_instance=RequestContext(request))

def register_event_guest(request, event_id):
    event = Event.objects.get(id=event_id)

    dates = []
    date = event.start_date
    while date <= event.end_date:
        dates.append(date)
        date += timedelta(days=1)

    RegistrationFormset = formset_factory(RegistrationStubForm, extra=0)
    GroupFormset = formset_factory(GroupStubForm, extra=0)
    MealFormset = formset_factory(MealStubForm, extra=len(dates))

    if request.method == 'POST':
        user_formset = RegistrationFormset(request.POST, prefix='user')
        group_formset = GroupFormset(request.POST, prefix='group')
        meal_formset = MealFormset(request.POST, prefix='meal')

        valid = False
        if group_formset.is_valid() and meal_formset.is_valid():
            if request.user.is_authenticated() or user_formset.is_valid():
                valid = True
        if valid:
            group_data = group_formset.cleaned_data[0]
            meal_data = meal_formset.cleaned_data

            if request.user.is_authenticated():
                user = request.user
                profile = user.get_profile()
            else:
                user_data = user_formset.cleaned_data[0]
                user = User.objects.create_user(
                    user_data['username'], 
                    user_data['email'], 
                    user_data['password']
                )

                authuser = authenticate(
                    username = user_data['username'], 
                    password = user_data['password']
                )
                login(request, authuser)

                profile = UserProfile.objects.create(
                    user            = user,
                    role            = 'A',
                )

            if profile.role == 'U' or not profile.role:
                profile.role = 'A'
                profile.save()

            group = Group.objects.create(
                name            = group_data['name'],
                url             = group_data['url'],
                description     = group_data['description'],
                role            = 'A'
            )

            gu = group.user(user)
            gu.admin            = True
            gu.save()

            eg = event.group(group)
            
            d = iter(dates)
            for m in meal_data:
                date = d.next()
                if 'members' in m:
                    meal = eg.meal(date,'D')
                    meal.members = m['members']
                    meal.features = ''.join(m['features'])
                    meal.notes = m['notes']
                    meal.save()
        
            return redirect('/logged-in/') # Redirect after POST
    else:
        user_formset = RegistrationFormset(prefix='user', initial=[{
            'role': 'A',
        }])
        group_formset = GroupFormset(prefix='group', initial=[{
            'role' : 'A',
        }])
        meal_formset = MealFormset(prefix='meal')

    return render_to_response('nourish/register_event_guest.html', {
        'request' : request,
        'user_formset' : user_formset,
        'group_formset' : group_formset,
        'meal_formset' : meal_formset,
        'event': event,
        'dates': iter(dates),
        'days': iter(dates),
        'next' : request.get_full_path(),
    }, context_instance=RequestContext(request))

