from nourish.forms.event import EventGroupHostFeaturesForm, EventGroupHostForm
from nourish.models import Event
from django.forms.formsets import formset_factory

import sys
from pprint import pformat

from fbcanvas.views import HybridCanvasView
from django.views.generic import TemplateView, DetailView

from nourish.views.register.group import EventGroupRegisterView

class EventHostRegisterView(EventGroupRegisterView):
    template_name = "nourish/EventGroupRegisterView.html"

    def default_role(self):
        return 'T'
        
    def get_context_data(self, **kwargs):
        context = super(EventHostRegisterView, self).get_context_data(**kwargs)

        GroupHostFormset = formset_factory(EventGroupHostForm, extra=0)
        FeaturesFormset = formset_factory(EventGroupHostFeaturesForm, extra=0)

        context['grouphost_formset'] = GroupHostFormset(prefix='grouphost', initial=[{
            'features' : [ 'd', 'p' ],
        }])
        context['features_formset'] = FeaturesFormset(prefix='features', initial=[{}])

        return context

    def get_post_formsets(self, request):
        formsets = super(EventHostRegisterView, self).get_post_formsets(request)

        GroupHostFormset = formset_factory(EventGroupHostForm, extra=0)
        FeaturesFormset = formset_factory(EventGroupHostFeaturesForm, extra=0)
        formsets['grouphost_formset'] = GroupHostFormset(request.POST, prefix='grouphost')
        formsets['features_formset'] = FeaturesFormset(request.POST, prefix='features')
    
        return formsets

    def formsets_valid(self, formsets):
        if not super(EventHostRegisterView, self).formsets_valid(formsets):
            return False
        if not formsets['grouphost_formset'].is_valid():
            return False
        if not formsets['features_formset'].is_valid():
            return False
        return True

    def save_changes(self, formsets):
        eg = super(EventHostRegisterView, self).save_changes(formsets)

        features_data = formsets['features_formset'].cleaned_data[0]
        grouphost_data = formsets['grouphost_formset'].cleaned_data[0]

        if 'features' in features_data:
            eg.features = ','.join(features_data['features'])
        if 'playa_address' in grouphost_data:
            eg.playa_address = grouphost_data['playa_address']
        if 'notes' in grouphost_data:
            eg.notes = grouphost_data['notes']
        eg.save()

        eg.showConfirm = True;

        return eg
