from django import forms
from nourish.models import EventUser, Event, GroupUser, Group, EventGroup
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.core.validators import ValidationError

class RegistrationForm(forms.Form):
    ROLE_CHOICES = (
        ('E', 'A regional event'),
        ('T', 'A theme camp'),
        ('A', 'An art project'),
    )

    def validate_username(username):
        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            return True

        raise ValidationError("This username already exists")

    username = forms.CharField(validators=[validate_username])
    url = forms.URLField(required=False, label="Personal Website", widget=forms.HiddenInput)
    email = forms.EmailField()
    phone = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label='Password Again')
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def clean(self):
        pw1 = self.cleaned_data.get("password")
        pw2 = self.cleaned_data.get("password2")
        if (pw1 != pw2):
            raise forms.ValidationError("passwords must match")
        return self.cleaned_data

class RegistrationStubForm(RegistrationForm):
    role = forms.CharField(widget=forms.HiddenInput)

class RegistrationKeyStubForm(RegistrationStubForm):
    def validate_key(key):
        if key not in [ "hungry" ]:
            raise ValidationError("This key is invalid")
    key = forms.CharField(label="Registration Key", validators=[validate_key])

class EventRegistrationForm(RegistrationForm):
    FEATURE_CHOICES = (
        ('v', 'Some Vegetarian'),
        ('V', 'Extensive Vegetarian'),
        ('e', 'Some Vegans'),
        ('E', 'Extensive Vegans'),
        ('g', 'Some Gluten Free'),
        ('G', 'Extensive Gluten Free'),
        ('D', 'Drinks Provided'),
        ('S', 'Service Provided'),
    )
    def validate_group_name(group_name):
        try:
            g = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            return True
        raise ValidationError("This group name already exists")

    role = forms.CharField(widget=forms.HiddenInput)
    group_name = forms.CharField(validators=[validate_group_name])
    group_url = forms.URLField(required=False, label="Group Website")
    arrival_date = forms.DateField(widget=SelectDateWidget)
    departure_date = forms.DateField(widget=SelectDateWidget)
    members = forms.IntegerField(required=False)
    dinner_time = forms.CharField(required=False)
    notes = forms.CharField(required=False)
    features = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=FEATURE_CHOICES,required=False)

