from django import forms
from django.forms import ModelForm
from nourish.models.group import Group, GroupUser

class GroupForm(ModelForm):
    class Meta:
        model = Group

    def save(self,commit=True):
        is_new = self.instance.pk is None
        r = super(GroupForm, self).save(commit)
        if is_new:
            Group.objects.add_admin(self.instance,self.request.user)
        return r

class GroupUserForm(ModelForm):
    class Meta:
        model = GroupUser

    def save(self,commit=True):
        if self.instance.pk is None:
            self.instance.user = self.request.user
        return super(GroupJoinForm, self).save(commit)
