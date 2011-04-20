from nourish.models.group import Group
from nourish.models.group import GroupUser

from nourish.models.event import Event
from nourish.models.event import EventUser
from nourish.models.event import EventGroup

from nourish.models.meal import Meal
from nourish.models.meal import MealInvite

from nourish.models.userprofile import UserProfile

from django.contrib import admin

admin.site.register(Group)
admin.site.register(GroupUser)

admin.site.register(Event)
admin.site.register(EventUser)
admin.site.register(EventGroup)

admin.site.register(Meal)
admin.site.register(MealInvite)

admin.site.register(UserProfile)
