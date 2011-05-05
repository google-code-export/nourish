from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from django.conf import settings
from nourish.views.canvas import HybridCanvasView
from nourish.models import Event
import urllib2
import cgi
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
        f = urllib2.urlopen("https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % ( settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY))
        token = cgi.parse_qs(f.read())["access_token"][-1]

        fb = facebook.GraphAPI(access_token=token)

        invites = []

        ids = self.request.GET['request_ids'].split(',')
        for i in ids:
#            if 'graph' not in self.request.facebook:
#                raise FacebookAuthTimeout
            notification = fb.get_object(i)
#            notification = self.request.facebook.graph.get_object(i)
            sys.stderr.write("request: " + pformat(notification) + "\n")
            try:
                d = json.loads(notification['data'])
                if 'type' in d:
                    if d['type'] == 'event_guest_invite':
                        invites.append(('nourish/site_invite/event_guest.html', { 
                            'from' : notification['from'], 
                            'event' : Event.objects.get(id=d['event']),  
                        }))
                    if d['type'] == 'event_host_invite':
                        invites.append(('nourish/site_invite/event_host.html', { 
                            'from' : notification['from'], 
                            'event' : Event.objects.get(id=d['event']),  
                        }))
                    if d['type'] == 'event_invite':
                        invites.append(('nourish/site_invite/event.html', { 
                            'from' : notification['from'], 
                            'event' : Event.objects.get(id=d['event']),  
                        }))
            except:
                continue

        context['invites'] = invites

        return context
