from django import forms
from socialregistration.forms import UserForm
from nourish.models import UserProfile

class SocialRegUserForm(UserForm):
    username = forms.RegexField(r'^[\w\@\.\+\-_]+$', max_length=32, required=False, widget=forms.HiddenInput)
    url = forms.URLField(required=False, widget=forms.HiddenInput)
    image_url = forms.URLField(required=False, widget=forms.HiddenInput)
    role = forms.CharField(widget=forms.HiddenInput, required=False)
    fullname = forms.CharField(max_length=50, label='Display Name')

    def save(self, request=None):
        r = super(SocialRegUserForm, self).save(request)

        user_profile = UserProfile.objects.create(
            user = self.user,
            fullname = self.cleaned_data.get('fullname'),
            url = self.cleaned_data.get('url'),
            role = self.cleaned_data.get('role'),
            provider = 'F',
        )

        if self.cleaned_data.get('link_profile'):
            user_profile.url = self.cleaned_data.get('url')
            user_profile.save()

        return r

class SocialRegUserFormHidden(SocialRegUserForm):
    fullname = forms.CharField(widget=forms.HiddenInput, required=False)
    email = forms.CharField(widget=forms.HiddenInput, required=False)
