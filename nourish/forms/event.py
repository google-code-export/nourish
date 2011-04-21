from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from nourish.models import Event

class EventForm(ModelForm):
    class Meta:
        model = Event
    start_date = forms.DateField(widget=SelectDateWidget)
    end_date = forms.DateField(widget=SelectDateWidget)
