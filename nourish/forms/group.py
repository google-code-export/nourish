from django import forms
from django.forms import ModelForm
from nourish.models import Group, GroupUser

class GroupForm(ModelForm):
    class Meta:
        model = Group

    def save(self,commit=True):
        is_new = self.instance.pk is None
        r = super(GroupForm, self).save(commit)
        if is_new:
            Group.objects.add_admin(self.instance,self.request.user)
        return r

class GroupJoinForm(ModelForm):
    class Meta:
        model = GroupUser

    def save(self,commit=True):
	print self.request.pk
        if self.instance.pk is None:
            self.instance.user = self.request.user
            self.instance.admin = False
        return super(GroupJoinForm, self).save(commit)

class GroupStubForm(GroupForm):
    role = forms.CharField(widget=forms.HiddenInput)
    description = forms.CharField(widget=forms.Textarea(attrs={'rows':3}))
