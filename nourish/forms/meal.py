from django import forms
from nourish.models import EventUser, Event, GroupUser, Group, EventGroup, Meal, MealInvite
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.core.validators import ValidationError
from django.forms import ModelForm

class EventGroupInviteForm(forms.Form):
    meals = forms.ModelMultipleChoiceField(queryset=Meal.objects.all(),widget=forms.CheckboxSelectMultiple)

class EventGroupInvitesForm(forms.Form):
    invite_id = forms.IntegerField(widget=forms.HiddenInput)
    action = forms.BooleanField(required=False)

class EventGroupMealForm(forms.Form):
    meal_id = forms.IntegerField(widget=forms.HiddenInput,required=False)
    meal = forms.CharField(widget=forms.HiddenInput)
    members = forms.IntegerField(widget=forms.TextInput(attrs={'size':'3'}), required=False)
    invite = forms.ChoiceField(choices=[], required=False)
    features = forms.ChoiceField(choices=[('', 'No'), ('R', 'Yes')], required=False)
    notes = forms.CharField(required=False)

class MealForm(ModelForm):
    class Meta:
        model = Meal

class MealStubForm(forms.Form):
    members = forms.IntegerField(widget=forms.TextInput(attrs={'size':3}), required=False)
    features = forms.ChoiceField(choices=( ('', 'No'), ('R', 'Yes')), required = False)
    notes = forms.CharField(required=False)
