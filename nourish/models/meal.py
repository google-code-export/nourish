from django.db import models
from django.contrib.auth.models import User
#from django.forms import ModelForm
from django import forms
from nourish.models.group import Group
#from nourish.models.event import Event, EventGroup

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
    features = models.CharField()
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
