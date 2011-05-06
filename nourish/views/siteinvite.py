from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from socialregistration.exceptions import FacebookAuthTimeout
from django.conf import settings
from nourish.views.canvas import HybridCanvasView
from nourish.models import Event
import urllib
import urllib2
import cgi
import facebook
from pprint import pformat
import sys
import json

class SiteInviteRecipientView(HybridCanvasView, TemplateView):
    context_object_name = 'siteinvite'
    template_name='nourish/site_invite_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SiteInviteRecipientView, self).get_context_data(**kwargs)
        if hasattr(self.request.facebook, 'graph'):
            graph = self.request.facebook.graph
        else:
            f = urllib2.urlopen("https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % ( settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY))
            token = cgi.parse_qs(f.read())["access_token"][-1]

            graph = facebook.GraphAPI(access_token=token)

        requests = []

        if 'request_ids' in self.request.GET:
            ids = self.request.GET['request_ids'].split(',')
            for i in ids:
                request = graph.get_object(i)
                requests.append(request)
        else:
            if not hasattr(self.request.facebook, 'user'):
                raise FacebookAuthTimeout
            args = {
                'format' : 'json',
                'access_token' : self.request.facebook.user['access_token'],
            }
            sys.stderr.write("uid %s\n" % self.request.facebook.uid)
            url = "https://graph.facebook.com/%s/apprequests?%s" % (self.request.facebook.uid, urllib.urlencode(args))
            f = urllib2.urlopen(url).read()
            d = json.loads(f)
            requests = d['data']
            
        sys.stderr.write("requests: " + pformat(requests) + "\n")

        invites = [] 

        for notification in requests:
            try:
                d = json.loads(notification['data'])
                if 'type' in d:
                    if d['type'] == 'event_guest_invite':
                        invites.append(('nourish/site_invite/event_guest.html', { 
                            'from' : notification['from'], 
                            'event' : Event.objects.get(id=d['event']),  
                        }))
                    elif d['type'] == 'event_host_invite':
                        invites.append(('nourish/site_invite/event_host.html', { 
                            'from' : notification['from'], 
                            'event' : Event.objects.get(id=d['event']),  
                        }))
                    else:
                        raise Exception("unknown type")
                else:
                    raise Exception("no type")
            except:
                invites.append(('nourish/site_invite/unknown.html', { 
                    'id' : notification['id'],
                    'from' : notification['from'], 
                    'data' : d,
                }))
                continue

        context['invites'] = invites

        return context
