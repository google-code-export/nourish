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
        n = self.get_notifications([request.POST['notification']])[0]
        if 'delete' in request.POST:
            n.remove()
        elif 'take_action' in request.POST:
            n.take_action()
        else:
            raise Exception("unknown method")

        return redirect(request.get_full_path())


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

#        return redirect('/nourish/fb/logged-in')

        if not len(context['notifications']):
            if 'canvas' in kwargs:
#                sys.stderr.write("in canvas\n")
                if request.user.is_authenticated():
                    return redirect('/nourish/fb/logged-in')
                else:
                    return redirect('/nourish/fb/')
            else:
#                sys.stderr.write("not in canvas\n")
                if request.user.is_authenticated():
                    return redirect('/nourish/logged-in')
                else:
                    return redirect('/nourish/')

        return super(NotificationListView, self).get(request, *args, **kwargs)

    def get_notifications(self, request_ids=None):
        return Notification.get_fb_notifications(None, request_ids)

    def get_context_data(self, **kwargs):
        context = super(NotificationListView, self).get_context_data(**kwargs)

        if 'request_ids' in self.request.GET:
            notifications = self.get_notifications(self.request.GET['request_ids'])
        else:
            notifications = self.request.user.get_profile().notifications()
            
        context['notifications'] = notifications

        return context

