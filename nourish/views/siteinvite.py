from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from nourish.views.canvas import HybridCanvasView
from nourish.models import Event
import facebook
from pprint import pformat
import sys
import json

class SiteInviteRecipientView(HybridCanvasView, TemplateView):
    context_object_name = 'siteinvite'
#    model = MealInvite
    template_name='nourish/site_invite_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SiteInviteRecipientView, self).get_context_data(**kwargs)

        invites = []

        ids = self.request.GET['request_ids'].split(',')
        for i in ids:
            notification = self.request.facebook.graph.get_object(i)
            sys.stderr.write("request: " + pformat(notification) + "\n")
            try:
                d = json.loads(notification['data'])
            except:
                continue
            if 'type' in d:
                if d['type'] == 'event_invite':
                    invites.append(('nourish/site_invite/event.html', { 'from' : notification['from'], 'event' : Event.objects.get(id=d['event']) }))

        context['invites'] = invites

        return context
