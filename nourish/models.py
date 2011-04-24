from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('U', 'Undefined'),
        ('E', 'Event Coordinator'),
        ('T', 'Theme Camp Organizer'),
        ('A', 'Art Project Organizer'),
    )
    fullname = models.CharField(max_length=50, verbose_name="Displayed Name", blank=True)
    url = models.URLField(blank=True, null=True, default='')
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='U')
    user = models.ForeignKey(User, unique=True)
    poweruser = models.BooleanField(default=False)

    def __unicode__(self):
        return self.fullname + ' (' + self.user.username + ')'

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
    role = models.CharField(max_length=1, choices=ROLE_CHOICES, default='U')
    description = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return '/groups/%i/' % self.id
    
    def user(self, user):
        try:
            gu = GroupUser.objects.get(user=user, group=self)
        except GroupUser.DoesNotExist:
            gu = GroupUser.objects.create(user=user, group=self)
        return gu

class Event(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Event Name')
    start_date = models.DateField(verbose_name='Event Begins')
    end_date = models.DateField(verbose_name='Event Ends')
    url = models.URLField(verbose_name='Event Website')
    display = models.BooleanField(default=False, verbose_name='Display in Event Lists')
#    logo = models.FileField(upload_to='uploads/%Y-%m-%d')
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return '/events/%i/' % self.id

    def group(self,group):
        try:
            eg = EventGroup.objects.get(event=event,group=group)
        except:
            eg = EventGroup.objects.create(
                event           = self,
                group           = group,
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
        return self.event.get_absolute_url() + 'group/%i/' % self.id 
    
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
        invite.state = 'S'
        invite.save()
        self.state = 'S'
        self.invite = invite
        self.save()
        invites = MealInvite.objects.filter(meal=self)
    
    def get_invite(self, host_eg):
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
