from django.shortcuts import redirect
from nourish.models import Group, Event
from nourish.forms.group import GroupForm, GroupFBForm
from nourish.forms.register import RegistrationStubForm
from socialregistration.exceptions import FacebookAuthTimeout
from datetime import timedelta
import datetime
from django.forms.formsets import formset_factory

import sys
from pprint import pformat

from fbcanvas.views import HybridCanvasView
from django.views.generic import TemplateView, DetailView
from nourish.views.register.base import FBRegisterView

class EventGroupRegisterView(FBRegisterView, HybridCanvasView, DetailView):
    context_object_name = 'event'
    model = Event

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        super(EventGroupRegisterView, self).post(request, *args, **kwargs)

        formsets = self.get_post_formsets(request)
        if not self.formsets_valid(formsets):
            formsets.update({
                'object' : self.object,
                'dates' : iter(self.get_dates()),
                'days' : iter(self.get_dates()),
            })
            return self.render_to_response(formsets)

        dest = self.save_changes(formsets)

        return redirect(dest.get_absolute_url(hasattr(request, 'fbcanvas') and request.fbcanvas))

    def default_role(self):
        return 'U'

    def get_context_data(self, **kwargs):
        context = super(EventGroupRegisterView, self).get_context_data(**kwargs)

        if self.is_fb():
            GroupFormset = formset_factory(GroupFBForm, extra=0)
            group_formset = GroupFormset(prefix='group', initial=[{ 'role' : self.default_role() }])
            group_formset[0].fields['group'].choices = self.get_group_choices(self.request.facebook.graph, self.object, self.request.user)
        else:
            GroupFormset = formset_factory(GroupForm, extra=0)
            group_formset = GroupFormset(prefix='group', initial=[{ 'role' : self.default_role() }])

        RegistrationFormset = formset_factory(RegistrationStubForm, extra=0)
        user_formset = RegistrationFormset(prefix='user', initial=[{ 'role': self.default_role() }])

        context['user_formset'] = user_formset
        context['group_formset'] = group_formset
        context['next'] = self.request.get_full_path()
        context['dates'] = iter(self.get_dates())
        context['days'] = iter(self.get_dates())

        return context

    def get_post_formsets(self, request):
        if self.is_fb():
            GroupFormset = formset_factory(GroupFBForm, extra=0)
            group_formset = GroupFormset(request.POST, prefix='group')
            group_formset[0].fields['group'].choices = self.get_group_choices(self.request.facebook.graph, self.get_object(), self.request.user)
        else:
            GroupFormset = formset_factory(GroupForm, extra=0)
            group_formset = GroupFormset(request.POST, prefix='group')

        RegistrationFormset = formset_factory(RegistrationStubForm, extra=0)
        user_formset = RegistrationFormset(request.POST, prefix='user')

        return {
            'user_formset' : user_formset,
            'group_formset' : group_formset, 
        }

    def formsets_valid(self, formsets):
        if not formsets['group_formset'].is_valid():
            return False
        if self.request.user.is_authenticated():
            return True
        if not formsets['user_formset'].is_valid():
            return False
        return True

    def save_changes(self, formsets):
        if self.request.user.is_authenticated():
            user = self.request.user
        else:
            user = self.newuser(formsets['user_formset'].cleaned_data[0], self.request)

        group_data = formsets['group_formset'].cleaned_data[0]

        profile = user.get_profile()
        if profile.role == 'U' or not profile.role:
            profile.role = self.default_role()
            profile.save()

        if self.is_fb():
            try:
                group = self.group_from_facebook(self.request.facebook.graph, group_data['group'], self.request.user)
                if group.role == 'U' or not group.role:
                    group.role = self.default_role(),
                    group.save()
            except AttributeError:
                raise FacebookAuthTimeout
        else:
            group = Group.objects.create(
                name            = group_data['name'],
                url             = group_data['url'],
                description     = group_data['description'],
                image_url       = group_data['image_url'],
                role            = self.default_role(),
            )

        gu = group.user(user)
        gu.admin = True
        gu.save()

        eg = self.object.group(group)
        eg.role = self.default_role()
        eg.save()

        return eg

    def get_dates(self):
        dates = []
        date = self.object.start_date
        while date <= self.object.end_date:
            dates.append(date)
            date += timedelta(days=1)
        return dates


