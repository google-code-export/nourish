from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from nourish.models import Event
from datetime import date, timedelta

class EventForm(ModelForm):
    class Meta:
        model = Event
    start_date = forms.DateField(widget=SelectDateWidget)
    end_date = forms.DateField(widget=SelectDateWidget)

    def clean(self):
        start = self.cleaned_data.get("start_date")
        end = self.cleaned_data.get("end_date")
        if start < date.today():
            raise forms.ValidationError("start date must be in the future!")
        if start > end:
            raise forms.ValidationError("start date must be after end date!")
        if (end - start) > timedelta(days=28):
            raise forms.ValidationError("event must not be longer than four weeks")
        return self.cleaned_data
