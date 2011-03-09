from django.db import models
from django.contrib.auth.models import User
#from django.forms import ModelForm
from django import forms
from nourish.models.group import Group

class Event(models.Model):
	name = models.CharField(max_length=100, unique=True)
	start_date = models.DateField()
	end_date = models.DateField()
	def __unicode__(self):
		return self.name
	def get_absolute_url(self):
		return '/events/%i/' % self.id
	def add_admin(self, admin):
		EventUser.objects.create(event=self, user=admin, admin=True, attend='M')
#	def attend(self, user, arrive):
#		EventUser.objects.create(event=self, user=user, attend='Y')

class EventUser(models.Model):
	ATTEND_CHOICES = (
		('Y', 'Yes'),
		('N', 'No'),
		('M', 'Maybe'),
	)
	event = models.ForeignKey(Event)
	user = models.ForeignKey(User)
	admin = models.BooleanField()
	group = models.ForeignKey(Group, null=True)
	attending = models.CharField(max_length=1, choices=ATTEND_CHOICES)
	arrival_date = models.DateField(null=True)
	departure_date = models.DateField(null=True)
	def __unicode__(self):
		return self.event.name + ' : ' + self.user.username

class EventGroup(models.Model):
	event = models.ForeignKey(Event)
	group = models.ForeignKey(Group)
	arrival_date = models.DateField()
	departure_date = models.DateField()
	expected_members = models.IntegerField()
	def __unicode__(self):
		return self.event.name + ' : ' + self.group.name
