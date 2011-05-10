from django.views.generic import TemplateView
from django.shortcuts import redirect
from nourish.views.canvas import HybridCanvasView
from nourish.models import Notification

class NotificationListView(HybridCanvasView, TemplateView):
    context_object_name = 'siteinvite'
    template_name='nourish/notification_list.html'

    def post(self, request, *args, **kwargs):
        if 'notification' not in request.POST:
            raise Exception("no notification specified")
        n = Notification.get_fb_notifications(facebook=request.facebook,request_ids=[request.POST['notification']])[0]
        if 'delete' in request.POST:
            n.remove()
        elif 'take_action' in request.POST:
            n.take_action()
        else:
            raise Exception("unknown method")
        return redirect(request.get_full_path())

    def get_user_notifications(self, facebook=None, request_ids=None):
        return Notification.get_fb_notifications(facebook, request_ids)

    def get_context_data(self, **kwargs):
        context = super(NotificationListView, self).get_context_data(**kwargs)

        if 'request_ids' in self.request.GET:
            notifications = self.get_user_notifications(request_ids = self.request.GET['request_ids'])
        else:
            notifications = self.get_user_notifications(facebook = self.request.facebook)
            
        invites = [] 

        context['notifications'] = notifications

        return context

