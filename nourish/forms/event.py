from django import forms
from django.forms import ModelForm
from django.forms.extras.widgets import SelectDateWidget
from nourish.models.event import Event, EventUser
from nourish.models.group import Group

class EventForm(ModelForm):
    class Meta:
        model = Event
    start_date = forms.DateField(widget=SelectDateWidget)
    end_date = forms.DateField(widget=SelectDateWidget)

    def save(self,commit=True):
        is_new = self.instance.pk is None
        r = super(EventForm, self).save(commit)
        if is_new:
            self.instance.add_admin(self.request.user)
#            Event.objects.add_admin(self.instance,self.request.user)
        return r

class EventAttendForm(ModelForm):
    class Meta:
        model = EventUser
	exclude = [ 'group' ]

    arrival_date = forms.DateField(widget=SelectDateWidget)
    departure_date = forms.DateField(widget=SelectDateWidget)

#    def save(self,commit=True):
#        r = super(EventAttendForm, self).save(commit)
#	return r
