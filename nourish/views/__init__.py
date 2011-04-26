from nourish.views.homepage import *
from nourish.views.register import *
from nourish.views.meal import *
from nourish.views.group import *
from nourish.views.event import *
from nourish.views.socialreg import social_reg_setup

#from socialregistration.signals import connect, login
#from socialregistration.models import FacebookProfile
#from django.core.signals import receiver
#import sys
#from pprint import pformat
#import facebook

#@receiver(login)
#def login_facebook(user, profile, client, **kwargs):
#    r = facebook.graph.get_object('me')
#    sys.stderr.write(pformat(r))

