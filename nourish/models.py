from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
import sys
from pprint import pformat
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
import json
from django.core.urlresolvers import reverse
import re
from socialregistration.models import FacebookProfile
from urlparse import parse_qs
import urllib2
import urllib
from facebook import GraphAPI

rewriter_re = re.compile("\/nourish\/")

def canvas_url_rewrite(url):
    return rewriter_re.sub('/nourish/fb/', url)

class FacebookProfileCache(models.Model):
    user = models.ForeignKey(User, unique=True)
    groups = models.TextField(blank=True)
    events = models.TextField(blank=True)
    last_updated = models.DateTimeField(blank=True, null=True)

    def get_groups(self):
        if self.groups:
            return json.loads(self.groups)
        else:
            return []

    def get_events(self):
        if self.events:
            return json.loads(self.events)
        else:
            return []

    def update(self, user, facebook):
        if not facebook.graph:
            return

        me = facebook.graph.get_object('me')
        try:
            link = me['link']
        except:
            link = 'http://www.facebook.com/profile.php?id=' + me['id']

        profile = user.get_profile()
        profile.fullname = me['name']
        profile.url = link
        profile.image_url = 'http://graph.facebook.com/' + me['id'] + '/picture'
        profile.save()

        fbgroups = facebook.graph.get_object('me/groups')
        groups = []
        for group in fbgroups['data']:
            groups.append((group['id'], group['name']))

        fbevents = facebook.graph.get_object('me/events')
        events = []
        now = datetime.datetime.now()
        for event in fbevents['data']:
            end = datetime.datetime.strptime(event['end_time'],"%Y-%m-%dT%H:%M:%S")
            if end > now:
                events.append((event['id'], event['name']))

        self.groups = json.dumps(groups)
        self.events = json.dumps(events)

        self.save()

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('U', 'Undefined'),
        ('E', 'Event Coordinator'),
        ('T', 'Theme Camp Organizer'),
        ('A', 'Art Project Organizer'),
    )
    PROVIDER_CHOICES = (
        ('U', 'Undefined'),
        ('N', 'None'),
        ('F', 'Facebook'),
    )
    fullname = models.CharField(max_length=50, verbose_name="Displayed Name", blank=True)
    url = models.URLField(blank=True, null=True, default='')
    image_url = models.URLField(blank=True, null=True, default='')
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='U')
    provider = models.CharField(max_length=1, choices=PROVIDER_CHOICES, default='N')
    user = models.ForeignKey(User, unique=True)
    poweruser = models.BooleanField(default=False)

    def __unicode__(self):
        return self.fullname + ' (' + self.user.username + ')'

    def fb_cache(self):
        if self.provider == 'U':
            self.provider = 'F'
            self.save()

        if self.provider != 'F':
            raise Exception("UserProfile.provider is not Facebook [%s]" % self.provider)
        try:
            fb_cache = FacebookProfileCache.objects.get(user=self.user)
        except FacebookProfileCache.DoesNotExist:
            fb_cache = FacebookProfileCache.objects.create(user=self.user)
        return fb_cache

    def admin_groups(self):
        groups = []
        for gm in GroupUser.objects.filter(user=self.user, admin=True):
            groups.append(gm.group)
        return groups

    def upcoming_events(self):
        my_events = list(EventUser.objects.filter(user=self.user,admin=True))
        groups = self.admin_groups()
        group_events = list(EventGroup.objects.filter(group__in=groups)) 
        have_events = { }
        events = []

        for eu in my_events:
            have_events[eu.event.id] = True
            events.append(eu.event)

        for eg in group_events:
            if eg.event.id not in have_events:
                events.append(eg.event)
                have_events[eg.event.id] = True
            
        out = []
        for event in events:
            out.append(event)
            for eg in group_events:
                if eg.event == event:
                    out.append(eg)
        return out

    def public_events(self):
        return list(Event.objects.filter(display=True))

class GroupUser(models.Model):
    group = models.ForeignKey('Group')
    user = models.ForeignKey(User)
    admin = models.BooleanField(default=False)
    def __unicode__(self):
        return self.group.name + ' : ' + self.user.username

class Group(models.Model):
    ROLE_CHOICES = (
        ('U', 'Undefined'),
        ('T', 'Theme Camp'),
        ('A', 'Artist Group'),
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="Group Name")
    url = models.CharField(max_length=250, blank=True, null=True, verbose_name="Group Website")
    image_url = models.URLField(blank=True, null=True, default='', verbose_name="Image URL")
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='U')
    description = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.name
    def get_absolute_url(self, canvas=False):
        u = reverse('group-detail', kwargs={'pk':self.id, 'slug': slugify(self.name)})
        if canvas:
            return canvas_url_rewrite(u)
        return u
    
    def user(self, user):
        try:
            gu = GroupUser.objects.get(user=user, group=self)
        except GroupUser.DoesNotExist:
            gu = GroupUser.objects.create(user=user, group=self)
        return gu

    def is_admin(self, user):
        if not user.is_authenticated():
            return False
        try:
            gu = GroupUser.objects.get(user=user, group=self, admin=True)
        except GroupUser.DoesNotExist:
            return False
        return True

class Event(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Event Name')
    start_date = models.DateField(verbose_name='Event Begins')
    end_date = models.DateField(verbose_name='Event Ends')
    url = models.URLField(verbose_name='Event Website')
    image_url = models.URLField(blank=True, null=True, default='', verbose_name="Image URL")
    display = models.BooleanField(default=False, verbose_name='Display in Event Lists')
#    logo = models.FileField(upload_to='uploads/%Y-%m-%d')
    def __unicode__(self):
        return self.name
    def get_absolute_url(self, canvas=False):
        u = reverse('event-detail', kwargs={'pk':self.id, 'slug': slugify(self.name)})
        if canvas:
            return canvas_url_rewrite(u)
        return u

    def is_admin(self, user):
        if not user.is_authenticated():
            return False
        try:
            gu = EventUser.objects.get(user=user, event=self, admin=True)
        except EventUser.DoesNotExist:
            return False
        return True

    def group(self,group):
        try:
            eg = EventGroup.objects.get(event=self,group=group)
        except EventGroup.DoesNotExist:
            eg = EventGroup.objects.create(
                event           = self,
                group           = group,
                role            = group.role,
            )
        return eg

    def user(self,user):
        try:
            u = EventUser.objects.get(event=self, user=user)
        except EventUser.DoesNotExist:
            u = EventUser.objects.create(
                event           = self, 
                user            = user,
            )
        return u

class EventUser(models.Model):
    event = models.ForeignKey(Event,editable=False)
    user = models.ForeignKey(User,editable=False)
    admin = models.BooleanField(editable=False, default=False)
    def __unicode__(self):
        return self.event.name + ' : ' + self.user.username

class EventGroup(models.Model):
    ROLE_CHOICES = (
        ('U', 'Undefined'),
        ('T', 'Theme Camp'),
        ('A', 'Artist Group'),
    )
    FEATURE_CHOICES = (
        ('v', 'Vegetarian Friendly'),
        ('e', 'Vegan Friendly'),
        ('g', 'Gluten Free'),
        ('r', 'Raw Friendly'),
        ('k', 'Kosher Friendly'),
        ('h', 'Halal'),
        ('d', 'Drinks Provided'),
        ('p', 'Plates/Utensils/Cups Provided'),
    )
    event = models.ForeignKey(Event)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='U')
    playa_address = models.CharField(max_length=50, blank=True, default='')
    dinner_time = models.CharField(max_length=10,null=True,blank=True)
    features = models.CharField(max_length=100, default='', choices=FEATURE_CHOICES)
    notes = models.TextField(blank=True, default='')
    def __unicode__(self):
        return self.event.name + ' : ' + self.group.name
    def get_absolute_url(self, canvas=False):
        u = reverse('event-group-detail', kwargs={'pk':self.id, 'slug': '%s-at-%s' % (slugify(self.group.name), slugify(self.event.name))})
        if canvas:
            return canvas_url_rewrite(u)
        return u
    
    def meal(self,date,meal):
        try:
            m = Meal.objects.get(eg=self, date=date, meal=meal)
        except Meal.DoesNotExist:
            m = Meal.objects.create(
                eg          = self,
                event       = self.event,
                date        = date,
                meal        = meal,
            )
        return m

    def send_notification(self, recipient, action, objects):
        sys.stderr.write("=== send notification [%s] from %s to %s with %d objects\n" % ( action, self.group.name, recipient.group.name, len(objects) ))

        msg = render_to_string("nourish/notif/%s.txt" % action, { 'object' : objects[0] })

        data = { 'action' : action, 'ot' : objects[0].__class__.__name__, 'objects' : [], 'type' : 'notif' }
        for o in objects:
            data['objects'].append(o.id)

        for gu in GroupUser.objects.filter(group=recipient.group,admin=True):
            if gu.user.get_profile().provider == 'F':
                Notification.send_fb(gu.user, msg, data)
            

    # host group sends invitations to guest groups
    def send_invites(self, meals):
        invites_by_eg = { }
        for meal in meals:
            if meal.eg not in invites_by_eg:
                invites_by_eg[meal.eg] = []
            invites_by_eg[meal.eg].append(meal.send_invite(self))
        # notify all guest groups
        for eg, invites in invites_by_eg.iteritems():
            self.send_notification(eg, 'invited', invites)

    # host group rescinds invitations
    def rescind_invites(self, invites):
        meals_by_eg = { }
        for invite in invites:
            if invite.meal.invite == invite:
                if invite.meal.eg not in meals_by_eg:
                    meals_by_eg[invite.meal.eg] = []
                meals_by_eg[invite.meal.eg].append(invite.meal)
            invite.rescind()
        # notify guest of any rescinded invites that were selected or confirmed
        for eg, meals in meals_by_eg.iteritems():
            self.send_notification(eg, 'rescinded', meals)

    # host group confirms invitations
    def confirm_invites(self, invites):
        invites_by_eg = { }
        for invite in invites:
            if invite.host_eg not in invites_by_eg:
                invites_by_eg[invite.host_eg] = []
            invites_by_eg[invite.host_eg].append(invite)
            invite.confirm()
        # notify guests
        for eg, invites in invites_by_eg.iteritems():
            self.send_notification(eg, 'confirmed', invites)

    # guest group chooses invitations
    def choose_invites(self, invites):
        invites_by_eg = { }
        for invite in invites:
            if invite.host_eg not in invites_by_eg:
                invites_by_eg[invite.host_eg] = []
            invites_by_eg[invite.host_eg].append(invite)
            invite.meal.choose(invite)
        # notify hosts
        for eg, invites in invites_by_eg.iteritems():
            self.send_notification(eg, 'chosen', invites)

    # guest group unchoose invitations
    def unchoose_meals(self, meals):
        meals_by_eg = { }
        for meal in meals:
            if meal.invite and meal.invite.state == 'C':
                if meal.invite.host_eg not in meals_by_eg:
                    meals_by_eg[meal.invite.host_eg] = []
                meals_by_eg[meal.invite.host_eg].append(meal)
            meal.unchoose()
        # notify hosts of any unchosen invites that were selected or confirmed
        for eg, meals in meals_by_eg.iteritems():
            self.send_notification(eg, 'unchosen', meals)

    # guest group deletes meals
    def delete_meals(self, meals):
        host_egs = { }
        for meal in meals:
            if meal.invite and meal.invite.state == 'C':
                host_egs[meal.invite.host_eg] = True
            meal.delete()
        # notify hosts of any deleted meals that were selected or confirmed
        for eg, j in host_egs.iteritems():
            self.send_notification(eg, 'deleted', eg)

    # guest adds meals
    def add_meals(self, meals):
        host_egs = { }
        for meal in meals:
            meal.save()
        # notify hosts that have sent any invites for any of the guests other meals
        for invite in MealInvite.objects.filter(guest_eg=self):
            if invite.host_eg not in host_egs:
                pass
#                self.send_notification(invite.host_eg, 'added', meals)
#                host_egs[invite.host_eg] = True

    # guest changes meals
    def change_meals(self, changes):
        invites_by_eg = { }
        for (meal, data) in changes:
            if meal.invite and meal.invite.state == 'C':
                if meal.invite.host_eg not in invites_by_eg:
                    invites_by_eg[meal.invite.host_eg] = []
                invites_by_eg[meal.invite.host_eg].append(meal.invite)
            meal.change(data)
        # notify hosts of any selected or confirmed invitations associated with changed meal
        for eg, invites in invites_by_eg.iteritems():
            self.send_notification(eg, 'changed', invites)

class MealInvite(models.Model):
    STATE_CHOICES = (
        ('N', 'New'),
        ('S', 'Selected'),
        ('C', 'Confirmed'),
        ('R', 'Rejected'),
    )
    date = models.DateField()
    event = models.ForeignKey('Event')
    host_eg = models.ForeignKey('EventGroup')
    guest_eg = models.ForeignKey('EventGroup', related_name='foo')
    meal = models.ForeignKey('Meal')
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default='N')
    def __unicode__(self):
        return str(self.date) + ' - ' + self.host_eg.group.name + ' (' + str(self.host_eg.dinner_time) + ', '  + self.host_eg.features + ') [' + self.state + ']'
    def rescind(self):
        invites = MealInvite.objects.filter(meal=self.meal)
        if self.meal.invite == self:
            for invite in invites:
                if invite == self:
                    continue
                invite.state = 'N'
                invite.save()
        if len(invites) > 1:
            if self.meal.invite == self:
                self.meal.state = 'I'
        else:
            self.meal.state = 'N'
        self.meal.invite = None
        self.meal.save()
        self.delete()

    def confirm(self):
        invites = MealInvite.objects.filter(meal=self.meal)
        for invite in invites:
            if invite == self:
                continue
            invite.state = 'R'
            invite.save()
        self.state = 'C'
        self.meal.invite = self
        self.meal.state = 'C'
        self.meal.save()
        self.save()

class Meal(models.Model):
    MEAL_CHOICES = (
        ('D', 'Dinner'),
    )
    STATE_CHOICES = (
        ('N', 'New'),
        ('I', 'Invited'),
        ('S', 'Selected'),
        ('C', 'Confirmed'),
    )
    date = models.DateField()
    meal = models.CharField(max_length=1, choices=MEAL_CHOICES, default='D')
    event = models.ForeignKey('Event')
    eg = models.ForeignKey('EventGroup')
    state = models.CharField(max_length=1, choices=STATE_CHOICES, default='N')
    members = models.IntegerField(default=0)
    features = models.CharField(max_length=40, default='')
    notes = models.CharField(max_length=100, null=True, blank=True)
    invite = models.ForeignKey('MealInvite', null=True, blank=True, related_name='invite_link')
    def __unicode__(self):
        return str(self.date) + ' - ' + self.eg.group.name + ' (' + str(self.members) + ' diners) [' + self.state + ']'

    def unchoose(self):
        invites = MealInvite.objects.filter(meal=self)
        for invite in invites:
            invite.state = 'N'
            invite.save()
        self.invite = None
        if len(invites) > 0:
            self.state = 'I'
        else:
            self.state = 'N'
        self.save()
    
    def choose(self, invite):
        invites = MealInvite.objects.filter(meal=self)
        for o_invite in invites:
            if o_invite != invite:
                o_invite.state = 'N'
                o_invite.save()
        invite.state = 'S'
        invite.save()
        self.state = 'S'
        self.invite = invite
        self.save()
    
    def send_invite(self, host_eg):
        invite = MealInvite.objects.create(
            meal = self,
            date = self.date, 
            host_eg = host_eg,
            guest_eg = self.eg,
            event = self.eg.event,
            state = 'N',
        )
        if self.state == 'N':
            self.state = 'I'
            self.save()
        return invite

    def change(self, data):
        self.members = data['members']
        self.members = data['members']
        self.features = ''.join(data['features'])
        self.notes = ''.join(data['notes'])
        self.save()


class Notification(object):
    def __init__(self, *args, **kwargs):
        for k in kwargs.keys():
            setattr(self,k,kwargs[k])

    @staticmethod
    def get_fb_notifications(facebook=None, request_ids=None):
        if facebook and hasattr(facebook, 'graph'):
            graph = facebook.graph
            token = facebook.user['access_token']
        else:
            token = self.get_fb_token()
            graph = GraphAPI(access_token=token)

        if request_ids:
            requests = []
            for i in request_ids:
                try:
                    parts = i.split('.')
                    if parts[0] == 'fb':
                        request = graph.get_object(parts[1])
                    else:
                        request = graph.get_object(i)
                    requests.append(request)
                except:
                    sys.stderr.write("bad id %s" % i)
        else:
            args = {
                'format' : 'json',
                'access_token' : token,
            }
            url = "https://graph.facebook.com/%s/apprequests?%s" % (facebook.uid, urllib.urlencode(args))
            f = urllib2.urlopen(url).read()
            d = json.loads(f)
            requests = d['data']

        notifications = []
        for request in requests:
            notifications.append(Notification.from_request(request))
        return notifications

    @staticmethod
    def from_request(request):
        d = json.loads(str(request['data']))
        if 'type' not in d:
            d['type'] = 'notif'
        if 'action' not in d:
            d['action'] = 'unknown'

        objclass = get_class('nourish.models.' + d['ot'])
        objects = []
        for o in d['objects']:
            try:
                objects.append(objclass.objects.get(id=o))
            except:
                pass

        return Notification(
            provider = 'F',
#            template = 'nourish/%s/%s.html' % (d['type'], d['action']),
            template = 'nourish/%s/%s.html' % ('notif', d['action']),
            type = 'notif',
            action = d['action'],
            id = 'fb.' + str(request['id']),
            objects = objects,
        )

    def take_action(self):
        if self.action == 'invited':
            self.objects[0].guest_eg.choose_invites(self.objects)
        elif self.action == 'chosen':
            self.objects[0].host_eg.confirm_invites(self.objects)
        else:
            raise Exception("nothing to do for this kind of notification [%s]" % self.action)
        self.remove()

    def remove(self):
        token = self.get_fb_token()
        graph = GraphAPI(access_token=token)
        path = "https://graph.facebook.com/%s?access_token=%s&method=delete" % (self.fb_id(), token)
        urllib2.urlopen(path).read()

    def fb_id(self):
        parts = self.id.split('.')
        return parts[1]

    @staticmethod
    def get_fb_token():
        return parse_qs(urllib2.urlopen("https://graph.facebook.com/oauth/access_token", urllib.urlencode({
            'client_id' : settings.FACEBOOK_APP_ID,
            'client_secret' : settings.FACEBOOK_SECRET_KEY,
            'grant_type' : 'client_credentials',
        })).read())['access_token'][-1]

    @staticmethod
    def send_fb(user, message, data):
        profile = FacebookProfile.objects.get(user=user)
        sys.stderr.write("sending to %s with %s [%s]\n" % (user, message, json.dumps(data)))
        urllib2.urlopen("https://graph.facebook.com/%s/apprequests" % profile.uid, urllib.urlencode({
            'message' : message,
            'data' : json.dumps(data),
            'access_token' : Notification.get_fb_token(),
        })).read()


# from http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m
