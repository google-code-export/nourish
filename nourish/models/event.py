from django.db import models
from django.contrib.auth.models import User
#from django.forms import ModelForm
#from django import forms
from nourish.models.group import Group
#from nourish.models.meal import Meal

class Event(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    end_date = models.DateField()
    url = models.URLField()
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
