from nourish.models import Event, Group, UserProfile, User, EventGroup
from socialregistration.exceptions import FacebookAuthTimeout
from django.contrib.auth import login, authenticate
from datetime import timedelta
import datetime
import iso8601

import sys
from pprint import pformat

class FBRegisterView(object):
    def is_fb(self):
        if not self.request.user.is_authenticated() or self.request.user.get_profile().provider != 'F':
            return False
        if 'nofb' in self.request.GET:
            return False
        try:
            if not self.request.facebook.user['uid']:
                return False
        except AttributeError:
            raise FacebookAuthTimeout
        return True

    def render_to_response(self, context):
        context['is_fb'] = self.is_fb()
        return super(FBRegisterView, self).render_to_response(context)

    def get_group_choices(self, graph, event, user):
        me = graph.get_object("me")
        groups = graph.request("me/groups", { "fields" : "owner,name" })
        events = graph.request("me/events", { "fields" : "owner,name" })
        accounts = graph.get_object("me/accounts")
        sys.stderr.write("me " + pformat(me) + "\n")
        sys.stderr.write("groups " + pformat(groups) + "\n")
        sys.stderr.write("events " + pformat(events) + "\n")
        sys.stderr.write("accounts " + pformat(accounts) + "\n")
        choices = []
        if self.can_select_group(me['name'], event, user):
            choices.append((me['id'], me['name'] + " (Me)"))
        for group in groups['data']:
            if 'owner' not in group or group['owner']['id'] != me['id']:
                continue
            if self.can_select_group(group['name'], event, user):
                choices.append((group['id'], group['name'] + " (Group)"))
        for e in events['data']:
            if 'owner' not in e or e['owner']['id'] != me['id']:
                continue
            if iso8601.parse_date(e['end_time']).replace(tzinfo=None) < datetime.datetime.utcnow():
                continue
            if self.can_select_group(e['name'], event, user):
                choices.append((e['id'], e['name'] + " (Event)"))
        for account in accounts['data']:
            if 'category' in account and 'name' in account and 'id' in account:
                if self.can_select_group(account['name'], event, user):
                    choices.append((account['id'], account['name'] + " (Page - " + account['category'] + ")"))
        return choices
    
    def can_select_group(self, name, event, user):
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
    
    def get_event_choices(self, graph):
        choices = []
        events = graph.get_object("me/events")
        for event in events['data']:
            if not Event.objects.filter(name=event['name']).count():
                choices.append((event['id'], event['name']))
        return choices
    
    def newuser(self, user_data, request):
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
        return user
    
    def event_from_facebook(self, graph, event_id, user):
        event_data = { }
        try:
            fbevent = graph.get_object(event_id)
        except:
            raise FacebookAuthTimeout
        event_data['name'] = fbevent['name']
        if 'link' in fbevent:
            event_data['url'] = fbevent['link']
        else:
            event_data['url'] = 'http://www.facebook.com/event.php?eid=' + str(fbevent['id'])
        event_data['image_url'] = 'http://graph.facebook.com/' + str(fbevent['id']) + '/picture'
        try:
            event = Event.objects.get(name=fbevent['name'])
            if not event.is_admin(user):
                raise Exception("you are not an admin of this event")
        except Event.DoesNotExist:
            event = Event.objects.create(
                end_date        = datetime.datetime.strptime(fbevent['end_time'],"%Y-%m-%dT%H:%M:%S").date() + timedelta(days=5),
                start_date      = datetime.datetime.strptime(fbevent['start_time'],"%Y-%m-%dT%H:%M:%S").date() - timedelta(days=10),
                name            = event_data['name'],
                url             = event_data['url'],
                image_url       = event_data['image_url'],
            )
    
        return event
    
    def group_from_facebook(self, graph, obj_id, user):
        group_data = { }
        try:
            fbgroup = graph.get_object(obj_id)
        except:
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
            if not group.is_admin(user):
                raise Exception("you are not an admin of this group")
        except Group.DoesNotExist:
            group = Group.objects.create(
                name            = group_data['name'],
                url             = group_data['url'],
                description     = group_data['description'],
                image_url       = group_data['image_url'],
                role            = 'U',
            )
        return group
