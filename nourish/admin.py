from nourish.models import Group
from nourish.models import GroupUser
from nourish.models import Event
from nourish.models import EventUser
from nourish.models import EventGroup
from nourish.models import Meal
from nourish.models import MealInvite
from nourish.models import UserProfile
from nourish.models import FacebookProfileCache
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from django.contrib import admin

class EventGroupInline(admin.TabularInline):
    model = EventGroup

class EventGroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'event', 'group', 'role')
    list_filter = ('event__name', 'role')
    list_per_page = 500
    ordering = ['-event', 'role', 'group']


class GroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'role')
    list_per_page = 500
    inlines = [
        EventGroupInline,
    ]

class MealInline(admin.TabularInline):
    model = Meal

class MealInviteAdmin(admin.ModelAdmin):
    list_display = ('date', 'event', 'host_eg', 'guest_eg', 'dinner_time', 'state')
    list_filter = ('date', 'event__name', 'state')
    list_per_page = 500
    inlines = [
        MealInline,
    ]

class UserInline(admin.TabularInline):
    model = User

class GroupUserAdmin(admin.ModelAdmin):
    list_per_page = 500
    inlines = [
        UserInline,
    ]

class MealAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'invite', 'state', 'members')
    list_filter = ('state', 'event__name')
    list_per_page = 500

UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'last_login', 'date_joined')

admin.site.register(Group, GroupAdmin)
admin.site.register(GroupUser, GroupUserAdmin)
admin.site.register(Event)
admin.site.register(EventUser)
admin.site.register(EventGroup, EventGroupAdmin)
admin.site.register(Meal, MealAdmin)
admin.site.register(MealInvite, MealInviteAdmin)
admin.site.register(UserProfile)
admin.site.register(FacebookProfileCache)
