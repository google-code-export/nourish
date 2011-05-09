from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from django.shortcuts import redirect
from socialregistration.exceptions import FacebookAuthTimeout
from socialregistration.models import FacebookProfile
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

    def post(self, request, *args, **kwargs):
        if request.POST['action'] == 'delete_fb_request':
#            access_token = cgi.parse_qs(urllib2.urlopen("https://graph.facebook.com/oauth/access_token", urllib.urlencode({
#                'client_id' : settings.FACEBOOK_APP_ID,
#                'client_secret' : settings.FACEBOOK_SECRET_KEY,
#                'grant_type' : 'client_credentials',
#            })).read())['access_token'][-1]
            path = "https://graph.facebook.com/%s?access_token=%s&method=delete" % (request.POST['invite'], request.facebook.user['access_token'])
#            path = "https://api.facebook.com/method/notifications.markRead?notification_ids=%s&access_token=%s" % (request.POST['invite'], request.facebook.user['access_token'])
            sys.stderr.write("hit " + path + "\n")
            f = urllib2.urlopen(path)
            f.read()
            return redirect(request.path)
        if request.POST['action'] == 'confirm_invite':
            raise Exception("confirm invite is not implemented")
        if request.POST['action'] == 'select_invite':
            raise Exception("select invite is not implemented")
        raise Exception("unknown action")

    def get_context_data(self, **kwargs):
        context = super(SiteInviteRecipientView, self).get_context_data(**kwargs)
        if hasattr(self.request.facebook, 'graph'):
            graph = self.request.facebook.graph
            if not self.request.user.is_authenticated():
                raise FacebookAuthTimeout
        else:
            if 'ref' in self.request.GET:
                raise FacebookAuthTimeout
            f = urllib2.urlopen("https://graph.facebook.com/oauth/access_token?client_id=%s&client_secret=%s&grant_type=client_credentials" % ( settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY))
            token = cgi.parse_qs(f.read())["access_token"][-1]

            graph = facebook.GraphAPI(access_token=token)

        requests = []

        if 'request_ids' in self.request.GET:
            ids = self.request.GET['request_ids'].split(',')
            for i in ids:
                try:
                    request = graph.get_object(i)
                    requests.append(request)
                except:
                    sys.stderr.write("bad id %s" % i)
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

        # if we have a notification for a user who has a profile in our site, then we
        # know we can force them to login.
        if not self.request.user.is_authenticated():
            for notification in requests:
                profs = FacebookProfile.objects.filter(uid = notification['to']['id'])
                if len(profs) > 0:
                    raise FacebookAuthTimeout()

        invites = [] 

        for notification in requests:
            try:
                d = json.loads(str(notification['data']))
                if 'type' in d:
                    if d['type'] == 'event_guest_invite':
                        invites.append(('nourish/site_invite/event_guest.html', { 
                            'from' : notification['from'], 
                            'event' : Event.objects.get(id=d['event']),  
                            'id' : notification['id'],
                        }))
                    elif d['type'] == 'event_host_invite':
                        invites.append(('nourish/site_invite/event_host.html', { 
                            'from' : notification['from'], 
                            'event' : Event.objects.get(id=d['event']),  
                            'id' : notification['id'],
                        }))
                    elif d['type'] == 'notif':
                        objclass = get_class('nourish.models.' + d['ot'])
                        objects = []
                        for o in d['objects']:
                            try:
                                objects.append(objclass.objects.get(id=o))
                            except:
                                pass
                        invites.append(('nourish/notif/%s.html' % d['action'], { 
                            'action' : d['action'],
                            'id' : notification['id'],
                            'objects' : objects,
                        }))
                    else:
                        raise Exception("unknown type")
                else:
                    raise Exception("no type")
            except FacebookAuthTimeout:
                if 'from' in notification:
                    invites.append(('nourish/site_invite/unknown.html', { 
                        'id' : notification['id'],
                        'from' : notification['from'],
                        'data' : d,
                    }))
                else:
                    invites.append(('nourish/notif/unknown.html', { 
                        'id' : notification['id'],
                        'data' : d,
                    }))
                continue

        context['invites'] = invites

        return context


# from http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m
