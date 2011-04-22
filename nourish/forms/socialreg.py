from django import forms
from socialregistration.forms import UserForm
from nourish.models import UserProfile

class SocialRegUserForm(UserForm):
    username = forms.RegexField(r'^[\w\@\.\+\-_]+$', max_length=32)
    link_profile = forms.BooleanField(required=False, initial=True, label='Link To Facebook Profile')
    url = forms.CharField(widget=forms.HiddenInput, required=False)
    role = forms.CharField(widget=forms.HiddenInput, required=False)

    def save(self, request=None):
        r = super(SocialRegUserForm, self).save(request)

        user_profile = UserProfile.objects.create(
            user = self.user,
            role = self.cleaned_data.get('role'),
        )

        if self.cleaned_data.get('link_profile'):
            user_profile.url = self.cleaned_data.get('url')
            user_profile.save()

        return r
