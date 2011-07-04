from nourish.forms.meal import MealStubForm
from django.forms.formsets import formset_factory

import sys
from pprint import pformat

from fbcanvas.views import HybridCanvasView
from django.views.generic import TemplateView, DetailView
from nourish.views.register.group import EventGroupRegisterView

class EventGuestRegisterView(EventGroupRegisterView):
    template_name = "nourish/EventGuestRegisterView.html"

    def default_role(self):
        return 'A'
        
    def get_context_data(self, **kwargs):
        context = super(EventGuestRegisterView, self).get_context_data(**kwargs)

        dates = self.get_dates()
        MealFormset = formset_factory(MealStubForm, extra=len(dates))
        meal_formset = MealFormset(prefix='meal')

        context['meal_formset'] = meal_formset

        return context

    def get_post_formsets(self, request):
        formsets = super(EventGuestRegisterView, self).get_post_formsets(request)

        MealFormset = formset_factory(MealStubForm, extra=0)
        formsets['meal_formset'] = MealFormset(request.POST, prefix='meal')
    
        return formsets

    def formsets_valid(self, formsets):
        if not super(EventGuestRegisterView, self).formsets_valid(formsets):
            return False
        if not formsets['meal_formset'].is_valid():
            return False
        return True

    def save_changes(self, formsets):
        eg = super(EventGuestRegisterView, self).save_changes(formsets)
        meal_data = formsets['meal_formset'].cleaned_data
        
        d = iter(self.get_dates())
        for m in meal_data:
            date = d.next()
            if 'members' in m:
                if m['members'] > 0:
                    meal = eg.meal(date,'D')
                    meal.members = m['members']
                    meal.features = ''.join(m['features'])
                    meal.notes = m['notes']
                    meal.save()

        eg.showConfirm = True
        
        return eg
