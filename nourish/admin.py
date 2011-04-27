from nourish.models import Group
from nourish.models import GroupUser
from nourish.models import Event
from nourish.models import EventUser
from nourish.models import EventGroup
from nourish.models import Meal
from nourish.models import MealInvite
from nourish.models import UserProfile
from nourish.models import FacebookProfileCache

from django.contrib import admin

admin.site.register(Group)
admin.site.register(GroupUser)
admin.site.register(Event)
admin.site.register(EventUser)
admin.site.register(EventGroup)
admin.site.register(Meal)
admin.site.register(MealInvite)
admin.site.register(UserProfile)
admin.site.register(FacebookProfileCache)
