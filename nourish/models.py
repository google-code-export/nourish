from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
import sys
from pprint import pformat
import datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
import json


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

    def update(self, facebook):
        if not facebook.graph:
            return

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
        if self.provider != 'F':
            raise Exception("UserProfile.provider is not Facebook")
        try:
            fb_cache = FacebookProfileCache.objects.get(user=self.user)
        except FacebookProfileCache.DoesNotExist:
            fb_cache = FacebookProfileCache.objects.create(user=self.user)
        return fb_cache

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
    url = models.URLField(blank=True, null=True, verbose_name="Group Website")
    image_url = models.URLField(blank=True, null=True, default='', verbose_name="Image URL")
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='U')
    description = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return '/g/%i-%s/' % (self.id, slugify(self.name))
    
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
    def get_absolute_url(self):
        return '/e/%i-%s/' % (self.id, slugify(self.name))

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
    event = models.ForeignKey(Event)
    group = models.ForeignKey(Group)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='U')
    features = models.CharField(max_length=100, default='')
    dinner_time = models.CharField(max_length=10,null=True,blank=True)
    def __unicode__(self):
        return self.event.name + ' : ' + self.group.name
    def get_absolute_url(self):
        return '/eg/%i-%s-at-%s/' % (self.id, slugify(self.group.name), slugify(self.event.name))
    
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
        for invite in invites:
            if invite == self:
                continue
            invite.state = 'N'
            invite.save()
        if len(invites) > 1:
            if self.state in [ 'S', 'C' ]:
                self.meal.state = 'I'
                self.meal.invite = None
            else:
                self.meal.state = 'S'
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
        invites = MealInvite.objects.filter(meal=self)
    
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

