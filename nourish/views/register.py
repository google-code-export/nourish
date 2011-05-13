from django.template import RequestContext

from django.shortcuts import render_to_response, redirect
from nourish.models import Event, Group, UserProfile, User, EventGroup
from nourish.forms.register import RegistrationKeyStubForm, RegistrationStubForm
from nourish.forms.group import GroupForm, GroupFBForm
from nourish.forms.meal import MealStubForm
from nourish.forms.event import EventForm, EventFBForm, EventGroupHostFeaturesForm, EventGroupHostForm
from socialregistration.exceptions import FacebookAuthTimeout
from django.contrib.auth import login, authenticate
from datetime import timedelta
import datetime
from django.forms.formsets import formset_factory
import array
import sys
from pprint import pformat
from django.core.urlresolvers import reverse

def register_event(request, canvas=False):
    is_fb = False
    if request.user.is_authenticated() and request.user.get_profile().provider == 'F':
        is_fb = True
    if 'nofb' in request.GET:
        is_fb = False
    if is_fb:
        EventFormset = formset_factory(EventFBForm, extra=0)
        if request.facebook.user['uid']:
            choices = get_event_choices(request.facebook.graph)
        else:
            choices = []
        sys.stderr.write("choices " + pformat(choices) + "\n")
    else:
        EventFormset = formset_factory(EventForm, extra=0)

    RegistrationFormset = formset_factory(RegistrationKeyStubForm, extra=0)
    if request.method == 'POST':
        user_formset = RegistrationFormset(request.POST, prefix='user')
        event_formset = EventFormset(request.POST, prefix='event')
        if is_fb:
            event_formset[0].fields['event'].choices = choices
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

            if is_fb:
                try:
                    fbevent = request.facebook.graph.get_object(event_data['event'])
                except AttributeError:
                    raise FacebookAuthTimeout
                event_data['name'] = fbevent['name']
                if 'link' in fbevent:
                    event_data['url'] = fbevent['link']
                else:
                    event_data['url'] = 'http://www.facebook.com/event.php?eid=' + str(fbevent['id'])
                event_data['image_url'] = 'http://graph.facebook.com/' + str(fbevent['id']) + '/picture'
                try:
                    event = Event.objects.get(name=fbevent['name'])
                    if not event.is_admin(request.user):
                        raise Exception("you are not an admin of this event")
                except Event.DoesNotExist:
                    event = Event.objects.create(
                        end_date        = datetime.datetime.strptime(fbevent['end_time'],"%Y-%m-%dT%H:%M:%S").date() + timedelta(days=5),
                        start_date      = datetime.datetime.strptime(fbevent['start_time'],"%Y-%m-%dT%H:%M:%S").date() - timedelta(days=10),
                        name            = event_data['name'],
                        url             = event_data['url'],
                        image_url       = event_data['image_url'],
                    )
                    eu = event.user(user)
                    eu.admin = True;
                    eu.save()
            else:
                event = Event.objects.create(
                    name            = event_data['name'],
                    start_date      = event_data['start_date'],
                    end_date        = event_data['end_date'],
                    url             = event_data['url'],
                    image_url       = event_data['image_url'],
                )
                eu = event.user(user)
                eu.admin = True;
                eu.save()

            return redirect(event.get_absolute_url(canvas))
    else:
        user_formset = RegistrationFormset(prefix='user', initial=[{
            'role' : 'E',
        }])
        event_formset = EventFormset(prefix='event', initial=[{ }])
        if is_fb:
            event_formset[0].fields['event'].choices = choices

    return render_to_response('nourish/register_event.html', {
        'request' : request,
        'user_formset' : user_formset,
        'event_formset' : event_formset,
        'next' : request.get_full_path(),
        'is_fb' : is_fb,
        'canvas' : canvas,
    }, context_instance=RequestContext(request))

def register_event_guest(request, event_id, canvas=False):
    event = Event.objects.get(id=event_id)

    dates = []
    date = event.start_date
    while date <= event.end_date:
        dates.append(date)
        date += timedelta(days=1)

    is_fb = False
    if request.user.is_authenticated() and request.user.get_profile().provider == 'F':
        is_fb = True
    if 'nofb' in request.GET:
        is_fb = False

    RegistrationFormset = formset_factory(RegistrationStubForm, extra=0)
    MealFormset = formset_factory(MealStubForm, extra=len(dates))
    if is_fb:
        GroupFormset = formset_factory(GroupFBForm, extra=0)
        choices = get_group_choices(request.facebook.graph, event, request.user)
        sys.stderr.write("choices " + pformat(choices) + "\n")
    else:
        GroupFormset = formset_factory(GroupForm, extra=0)

    if request.method == 'POST':
        user_formset = RegistrationFormset(request.POST, prefix='user')
        group_formset = GroupFormset(request.POST, prefix='group')
        meal_formset = MealFormset(request.POST, prefix='meal')
        if is_fb:
            group_formset[0].fields['group'].choices = choices

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

#                profile = UserProfile.objects.create(
#                    user            = user,
#                    role            = 'A',
#                )

            profile = user.get_profile()

            if profile.role == 'U' or not profile.role:
                profile.role = 'A'
                profile.save()

            group = None

            if is_fb:
                try:
                    fbgroup = request.facebook.graph.get_object(group_data['group'])
                except AttributeError:
                    raise FacebookAuthTimeout
                group_data['name'] = fbgroup['name']
                if 'link' in fbgroup:
                    group_data['url'] = fbgroup['link']
                else:
                    group_data['url'] = 'http://www.facebook.com/group.php?gid=' + str(fbgroup['id'])
                group_data['image_url'] = 'http://graph.facebook.com/' + str(fbgroup['id']) + '/picture'
                if 'description' not in group_data:
                    group_data['description'] = ''
                try:
                    group = Group.objects.get(name=fbgroup['name'])
                    if not group.is_admin(request.user):
                        raise Exception("you are not an admin of this group")
                except Group.DoesNotExist:
                    group = Group.objects.create(
                        name            = group_data['name'],
                        url             = group_data['url'],
                        description     = group_data['description'],
                        image_url       = group_data['image_url'],
                        role            = 'A',
                    )
                    gu = group.user(user)
                    gu.admin            = True
                    gu.save()
            else:
                group = Group.objects.create(
                    name            = group_data['name'],
                    url             = group_data['url'],
                    description     = group_data['description'],
                    image_url       = group_data['image_url'],
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
        
            return redirect(eg.get_absolute_url(canvas))
    else:
        user_formset = RegistrationFormset(prefix='user', initial=[{
            'role': 'A',
        }])
        group_formset = GroupFormset(prefix='group', initial=[{
            'role' : 'A',
        }])
        if is_fb:
            group_formset[0].fields['group'].choices = choices
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
        'is_fb' : is_fb,
        'canvas' : canvas
    }, context_instance=RequestContext(request))

def register_event_host(request, event_id, canvas=False):
    event = Event.objects.get(id=event_id)

    dates = []
    date = event.start_date
    while date <= event.end_date:
        dates.append(date)
        date += timedelta(days=1)

    is_fb = False
    if request.user.is_authenticated() and request.user.get_profile().provider == 'F':
        is_fb = True
    if 'nofb' in request.GET:
        sys.stderr.write("notauth")
        is_fb = False

    RegistrationFormset = formset_factory(RegistrationStubForm, extra=0)
    GroupHostFormset = formset_factory(EventGroupHostForm, extra=0)
    FeaturesFormset = formset_factory(EventGroupHostFeaturesForm, extra=0)
    if is_fb:
        GroupFormset = formset_factory(GroupFBForm, extra=0)
        choices = get_group_choices(request.facebook.graph, event, request.user)
        sys.stderr.write("choices " + pformat(choices) + "\n")
    else:
        GroupFormset = formset_factory(GroupForm, extra=0)

    if request.method == 'POST':
        user_formset = RegistrationFormset(request.POST, prefix='user')
        group_formset = GroupFormset(request.POST, prefix='group')
        grouphost_formset = GroupHostFormset(request.POST, prefix='grouphost')
        features_formset = FeaturesFormset(request.POST, prefix='features')
        if is_fb:
            group_formset[0].fields['group'].choices = choices

        valid = False
        if group_formset.is_valid() and features_formset.is_valid():
            if request.user.is_authenticated() or user_formset.is_valid():
                valid = True
        if valid:
            group_data = group_formset.cleaned_data[0]
            grouphost_data = grouphost_formset.cleaned_data[0]
            features_data = features_formset.cleaned_data[0]

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
                    role            = 'T',
                )

            if profile.role == 'U' or not profile.role:
                profile.role = 'T'
                profile.save()

            group = None

            if is_fb:
                try:
                    fbgroup = request.facebook.graph.get_object(group_data['group'])
                except AttributeError:
                    raise FacebookAuthTimeout
                group_data['name'] = fbgroup['name']
                if 'link' in fbgroup:
                    group_data['url'] = fbgroup['link']
                else:
                    group_data['url'] = 'http://www.facebook.com/group.php?gid=' + str(fbgroup['id'])
                group_data['image_url'] = 'http://graph.facebook.com/' + str(fbgroup['id']) + '/picture'
                try:
                    group = Group.objects.get(name=fbgroup['name'])
                    if not group.is_admin(request.user):
                        raise Exception("you are not an admin of this group")
                except Group.DoesNotExist:
                    group = Group.objects.create(
                        name            = group_data['name'],
                        url             = group_data['url'],
                        image_url       = group_data['image_url'],
                        role            = 'T',
                    )
                    gu = group.user(user)
                    gu.admin            = True
                    gu.save()
            else:
                group = Group.objects.create(
                    name            = group_data['name'],
                    url             = group_data['url'],
                    description     = group_data['description'],
                    image_url       = group_data['image_url'],
                    role            = 'T'
                )
                gu = group.user(user)
                gu.admin            = True
                gu.save()

            eg = event.group(group)
            if 'features' in features_data:
                eg.features = ','.join(features_data['features'])
            eg.dinner_time = grouphost_data['dinner_time']
            if 'playa_address' in grouphost_data:
                eg.playa_address = grouphost_data['playa_address']
            if 'notes' in grouphost_data:
                eg.notes = grouphost_data['notes']
            eg.save()
            
            return redirect(eg.get_absolute_url(canvas))
    else:
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
            group_formset[0].fields['group'].choices = choices

    return render_to_response('nourish/register_event_host.html', {
        'request' : request,
        'user_formset' : user_formset,
        'group_formset' : group_formset,
        'grouphost_formset' : grouphost_formset,
        'features_formset' : features_formset,
        'event': event,
        'dates': iter(dates),
        'days': iter(dates),
        'next' : request.get_full_path(),
        'is_fb' : is_fb,
        'canvas' : canvas,
        'scroll_select' : is_fb and len(choices) > 3,
    }, context_instance=RequestContext(request))

def get_group_choices(graph, event, user):
    me = graph.get_object("me")
    groups = graph.get_object("me/groups")
    events = graph.get_object("me/events")
    accounts = graph.get_object("me/accounts")
    sys.stderr.write("me " + pformat(me) + "\n")
    sys.stderr.write("groups " + pformat(groups) + "\n")
    sys.stderr.write("events " + pformat(events) + "\n")
    sys.stderr.write("accounts " + pformat(accounts) + "\n")
    choices = []
    if can_select_group(me['name'], event, user):
        choices.append((me['id'], me['name'] + " (Me)"))
    for group in groups['data']:
        if can_select_group(group['name'], event, user):
            choices.append((group['id'], group['name'] + " (Group)"))
    for e in events['data']:
        if can_select_group(e['name'], event, user):
            choices.append((e['id'], e['name'] + " (Event)"))
    for account in accounts['data']:
        if 'category' in account and 'name' in account and 'id' in account:
            if can_select_group(account['name'], event, user):
                choices.append((account['id'], account['name'] + " (Page - " + account['category'] + ")"))
    return choices

def can_select_group(name, event, user):
    try:
        sys.stderr.write("\n===look for name %s at event %s user %s\n" % (name, event.id, user))
        g = Group.objects.get(name=name)
        sys.stderr.write("\n==got group\n")
        if not g.is_admin(user):
            sys.stderr.write("%s is not admin for %s\n" % (user, g))
            return False
        sys.stderr.write("%s is admin for %s\n" % (user, g))
        eg = EventGroup.objects.get(group=g, event=event)
        return False
    except:
        return True

def get_event_choices(graph):
    choices = []
    events = graph.get_object("me/events")
    for event in events['data']:
        if not Event.objects.filter(name=event['name']).count():
            choices.append((event['id'], event['name']))
    return choices
