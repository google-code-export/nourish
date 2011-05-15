from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from nourish.models import Event, EventGroup
from datetime import date, timedelta

class EventForm(ModelForm):
    class Meta:
        model = Event
        exclude = ('display')
    start_date = forms.DateField(widget=SelectDateWidget)
    end_date = forms.DateField(widget=SelectDateWidget)

    def clean(self):
        start = self.cleaned_data.get("start_date")
        end = self.cleaned_data.get("end_date")
        if not start or not end:
            raise forms.ValidationError("dates must be specified")
        if start < date.today():
            raise forms.ValidationError("start date must be in the future!")
        if start > end:
            raise forms.ValidationError("start date must be after end date!")
        if (end - start) > timedelta(days=28):
            raise forms.ValidationError("event must not be longer than four weeks")
        return self.cleaned_data

class EventFBForm(forms.Form):
    event = forms.ChoiceField(required=False,choices=[])

class EventGroupHostFeaturesForm(forms.Form):
    features = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,required=False,choices=EventGroup.FEATURE_CHOICES)

class EventGroupHostForm(ModelForm):
    class Meta:
        model = EventGroup
        exclude = ('event','group','role','features')

class EventInviteDayForm(forms.Form):
    date = forms.CharField(widget=forms.HiddenInput)
    dinner_time = forms.TimeField(required=False)

class EventInviteMealForm(forms.Form):
    meal_id = forms.CharField(widget=forms.HiddenInput)
    invited = forms.BooleanField(required=False)
