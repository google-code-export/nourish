from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from django.shortcuts import redirect
from socialregistration.exceptions import FacebookAuthTimeout
from socialregistration.models import FacebookProfile
from django.conf import settings
from nourish.views.canvas import HybridCanvasView
from nourish.models import Notification
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
        if 'notification' not in request.POST:
            raise Exception("no notification specified")
        n = Notification.get_notifications(facebook=request.facebook,request_ids=[request.POST['notification']])[0]
        if 'delete' in request.POST:
            n.remove()
        elif 'take_action' in request.POST:
            n.take_action()
        else:
            raise Exception("unknown method")
        return redirect(request.get_full_path())

    def get_user_notifications(self, facebook=None, request_ids=None):
        return Notification.get_notifications(facebook, request_ids)

    def get_context_data(self, **kwargs):
        context = super(SiteInviteRecipientView, self).get_context_data(**kwargs)

        if 'request_ids' in self.request.GET:
            notifications = self.get_user_notifications(request_ids = self.request.GET['request_ids'])
        else:
            notifications = self.get_user_notifications(facebook = self.request.facebook)
            
        invites = [] 

        context['notifications'] = notifications

        return context

# from http://stackoverflow.com/questions/452969/does-python-have-an-equivalent-to-java-class-forname
def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m
