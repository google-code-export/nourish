from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from nourish.forms.socialreg import SocialRegUserForm, SocialRegUserFormHidden
from socialregistration.views import setup
import sys
from pprint import pformat

def social_reg_setup(request):
    try:
        me = request.facebook.graph.get_object('me', fields='name,email,link')
        sys.stderr.write("fb: " + pformat(me))
    except AttributeError:
        me = { 'username' : '', 'email' : '', 'link' : ''}

    initial = { }
    if 'id' in me:
        initial['username'] = 'fb.' + str(me['id'])
        initial['image_url'] = 'http://graph.facebook.com/' + me['id'] + '/picture'
    if 'name' in me:
        initial['fullname'] = me['name']
    if 'email' in me:
        initial['email'] = me['email']
    if 'link' in me:
        initial['url'] = me['link']

    if 'nolink' in request.GET:
        form_class = SocialRegUserForm
        template = 'socialregistration/setup_nolink.html'
    else:
        form_class = SocialRegUserFormHidden
        template = 'socialregistration/setup.html'
    
    context = { }

    return setup(request, form_class=form_class, initial=initial, extra_context=context, template=template)

