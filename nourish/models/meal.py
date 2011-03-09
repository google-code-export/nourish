from django.db import models
from django.contrib.auth.models import User
from nourish.models.event import Event,EventGroup
from django.forms import ModelForm
from django import forms

class MealRequest(models.Model):
	MEAL_CHOICES = (
		('B', 'Breakfast'),
		('L', 'Lunch'),
		('D', 'Dinner'),
	)
	eventgroup = models.ForeignKey(EventGroup)
	date = models.DateField()
	meal = models.CharField(max_length=1, choices=MEAL_CHOICES)
	expected_diners = models.IntegerField()
	def __unicode__(self):
		return self.eventgroup.group.name + ' : ' + self.eventgroup.event.name + ' : ' + self.date + ' : ' + self.meal

class Meal(models.Model):
	MEAL_CHOICES = (
		('B', 'Breakfast'),
		('L', 'Lunch'),
		('D', 'Dinner'),
	)
	eventgroup = models.ForeignKey(EventGroup)
	date = models.DateField()
	meal = models.CharField(max_length=1, choices=MEAL_CHOICES)

class MealInvite(models.Model):
	meal = models.ForeignKey(Meal)
	mealrequest = models.ForeignKey(MealRequest)
