from django.shortcuts import redirect
from nourish.models import Event, Group
from nourish.forms.register import RegistrationKeyStubForm, RegistrationStubForm
from nourish.forms.group import GroupForm, GroupFBForm
from nourish.forms.meal import MealStubForm
from nourish.forms.event import EventForm, EventFBForm, EventGroupHostFeaturesForm, EventGroupHostForm
from socialregistration.exceptions import FacebookAuthTimeout
from datetime import timedelta
import datetime
from django.forms.formsets import formset_factory

import sys
from pprint import pformat

from fbcanvas.views import HybridCanvasView
from django.views.generic import TemplateView, DetailView

from nourish.views.register.base import FBRegisterView

class EventRegisterView(FBRegisterView, HybridCanvasView, TemplateView):
    template_name = 'nourish/EventRegisterView.html'

    def get_context_data(self, **kwargs):
        context = super(EventRegisterView, self).get_context_data(**kwargs)

        if self.is_fb():
            EventFormset = formset_factory(EventFBForm, extra=0)
            event_formset = EventFormset(prefix='event', initial=[{}])
            event_formset[0].fields['event'].choices = self.get_event_choices(self.request.facebook.graph)
        else:
            EventFormset = formset_factory(EventForm, extra=0)
            event_formset = EventFormset(prefix='event', initial=[{}])

        RegistrationFormset = formset_factory(RegistrationKeyStubForm, extra=0)
        user_formset = RegistrationFormset(prefix='user', initial=[{
            'role' : 'E',
        }])

        context['user_formset'] = user_formset
        context['event_formset'] = event_formset

        return context

    def post(self, request, *args, **kwargs):
        super(EventRegisterView, self).post(request, *args, **kwargs)
        if self.is_fb():
            EventFormset = formset_factory(EventFBForm, extra=0)
            event_formset = EventFormset(request.POST, prefix='event')
            event_formset[0].fields['event'].choices = self.get_event_choices(self.request.facebook.graph)
        else:
            EventFormset = formset_factory(EventForm, extra=0)
            event_formset = EventFormset(request.POST, prefix='event')

        RegistrationFormset = formset_factory(RegistrationKeyStubForm, extra=0)
        user_formset = RegistrationFormset(request.POST, prefix='user')
        valid = False
        if event_formset.is_valid() and (request.user.is_authenticated() or user_formset.is_valid()):
            event_data = event_formset.cleaned_data[0];

            if request.user.is_authenticated():
                user = request.user
            else:
                user = self.newuser(user_formset.cleaned_data[0], request)

            profile = user.get_profile()
            if profile.role == 'U' or not profile.role:
                profile.role = 'E'
                profile.save()

            if self.is_fb():
                try:
                    event = self.event_from_facebook(request.facebook.graph, event_data['event'], request.user)
                except AttributeError:
                    raise FacebookAuthTimeout
            else:
                event = Event.objects.create(
                    name            = event_data['name'],
                    start_date      = event_data['start_date'],
                    end_date        = event_data['end_date'],
                    url             = event_data['url'],
                    image_url       = event_data['image_url'],
                )
            eu = event.user(user)
            eu.admin = True;
            eu.save()

            return redirect(event.get_absolute_url(hasattr(request, 'fbcanvas') and request.fbcanvas))
        else:
            return self.render_to_response({
                'user_formset' : user_formset,
                'event_formset' : event_formset,
            })

