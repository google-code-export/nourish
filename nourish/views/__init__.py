from nourish.views.homepage import *
from nourish.views.register import *
from nourish.views.meal import *
from nourish.views.group import *
from nourish.views.event import *
from nourish.views.socialreg import social_reg_setup
from nourish.views.siteinvite import *
from django.db.models import signals
from django.contrib.auth.models import User

from socialregistration.signals import connect, login
#from socialregistration.models import FacebookProfile
from django.dispatch import receiver
import sys
from pprint import pformat
#import facebook

@receiver(login)
def login_facebook(user, profile, client, **kwargs):
    sys.stderr.write("facebook login\n")
    user.get_profile().fb_cache().update(user, client)

@receiver(connect)
def connect_facebook(user, profile, client, **kwargs):
    sys.stderr.write("facebook connect\n")
    user.get_profile().fb_cache().update(user, client)

@receiver(signals.post_save)
def saved_handler(instance, created, **kwargs):
    if isinstance(instance, User) and created:
        profile = UserProfile.objects.create(
            user = instance,
            role = 'U',
            provider = 'U',
        )

