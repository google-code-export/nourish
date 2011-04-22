from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from nourish.forms.socialreg import SocialRegUserForm
from socialregistration.views import setup

def social_reg_setup(request):
    try:
        me = request.facebook.graph.get_object('me')
    except AttributeError:
        me = { 'username' : '', 'email' : '', 'link' : ''}

    initial = { }
    if 'username' in me:
        initial['username'] = me['username']
    if 'email' in me:
        initial['email'] = me['email']
    if 'link' in me:
        initial['url'] = me['link']
        initial['link_profile'] = True

    return setup(request, form_class=SocialRegUserForm, initial=initial)
