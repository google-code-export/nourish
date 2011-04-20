from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('E', 'Event Coordinator'),
        ('T', 'Theme Camp Organizer'),
        ('A', 'Art Project Organizer'),
    )
    url = models.URLField()
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    user = models.ForeignKey(User, unique=True)
    def __unicode__(self):
        return self.user.username

class GroupManager(models.Manager):
    def add_admin(self, group, admin):
        GroupUser.objects.create(group=group, user=admin, admin=True)

class GroupUser(models.Model):
    group = models.ForeignKey('Group')
    user = models.ForeignKey(User)
    admin = models.BooleanField()
    def __unicode__(self):
        return self.group.name + ' : ' + self.user.username

class Group(models.Model):
    ROLE_CHOICES = (
        ('T', 'Theme Camp'),
        ('A', 'Artist Group'),
    )
    name = models.CharField(max_length=100, unique=True, verbose_name="Group Name")
    objects = GroupManager()
    url = models.URLField(blank=True, null=True, verbose_name="Group Website")
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    members = models.IntegerField(blank=True, null=True)
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
#    logo = models.FileField(upload_to='uploads/%Y-%m-%d')
    def __unicode__(self):
        return self.name
    def get_absolute_url(self):
        return '/events/%i/' % self.id
    def add_admin(self, admin):
        EventUser.objects.create(event=self, user=admin, admin=True, attending='M',arrival_date=self.start_date,departure_date=self.end_date,arrival_meal='D',departure_meal = 'B')

    def group(self,group):
        try:
            eg = EventGroup.objects.get(event=event,group=group)
        except:
            eg = EventGroup.objects.create(
                event           = self,
                group           = group,
                arrival_date    = self.start_date,
                departure_date  = self.end_date,
                expected_members= 0,
                attending       = 'Y',
                role            = '',
                features        = '',
                notes           = '',
            )
        return eg

    def user(self,user):
        try:
            u = EventUser.objects.get(event=self, user=user)
        except EventUser.DoesNotExist:
            u = EventUser.objects.create(
                event           = self, 
                user            = user,
                arrival_date    = self.start_date,
                departure_date  = self.end_date,
                arrival_meal    = 'B',
                departure_meal  = 'D',
                attending       = 'Y',
            )
        return u

class EventUser(models.Model):
    ATTEND_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
        ('M', 'Maybe'),
    )
    MEAL_CHOICES = (
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
    )
    event = models.ForeignKey(Event,editable=False)
    user = models.ForeignKey(User,editable=False)
    admin = models.BooleanField(editable=False)
    group = models.ForeignKey(Group, blank=True, null=True)
    attending = models.CharField(max_length=1, choices=ATTEND_CHOICES)
    arrival_date = models.DateField(null=True)
    departure_date = models.DateField(null=True)
    arrival_meal = models.CharField(max_length=1, choices=MEAL_CHOICES)
    departure_meal = models.CharField(max_length=1, choices=MEAL_CHOICES)
    def __unicode__(self):
        return self.event.name + ' : ' + self.user.username

class EventGroup(models.Model):
    ATTEND_CHOICES = (
        ('Y', 'Yes'),
        ('N', 'No'),
    )
    ROLE_CHOICES = (
        ('T', 'Theme Camp'),
        ('A', 'Artist Group'),
    )
    event = models.ForeignKey(Event)
    group = models.ForeignKey(Group)
    arrival_date = models.DateField()
    departure_date = models.DateField()
    expected_members = models.IntegerField()
    attending = models.CharField(max_length=1, choices=ATTEND_CHOICES)
    role = models.CharField(max_length=1, choices=ROLE_CHOICES)
    features = models.CharField(max_length=100)
    dinner_time = models.CharField(max_length=10,null=True,blank=True)
    notes = models.TextField()
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
                state       = 'N',
                members     = self.expected_members,
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
    state = models.CharField(max_length=1, choices=STATE_CHOICES)
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
        ('B', 'Breakfast'),
        ('L', 'Lunch'),
        ('D', 'Dinner'),
    )
    STATE_CHOICES = (
        ('N', 'New'),
        ('I', 'Invited'),
        ('S', 'Selected'),
        ('C', 'Confirmed'),
    )
    date = models.DateField()
    meal = models.CharField(max_length=1, choices=MEAL_CHOICES)
    event = models.ForeignKey('Event')
    eg = models.ForeignKey('EventGroup')
    state = models.CharField(max_length=1, choices=STATE_CHOICES)
    members = models.IntegerField()
    features = models.CharField(max_length=40)
    notes = models.CharField(max_length=100)
    invite = models.ForeignKey('MealInvite', null=True, blank=True)
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
    
    def invite(self, host_eg):
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
