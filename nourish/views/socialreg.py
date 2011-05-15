from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from nourish.forms.socialreg import SocialRegUserForm, SocialRegUserFormHidden
from socialregistration.views import setup
import sys
from pprint import pformat

def social_reg_setup(request):
    r = setup(request, form_class=form_class, initial=initial, extra_context=context, template=template)

