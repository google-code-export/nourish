from django import forms
from django.forms import ModelForm
from nourish.models import Group

class GroupForm(ModelForm):
    class Meta:
        model = Group
        exclude = ('role')
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
