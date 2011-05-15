from django.views.generic import DetailView, UpdateView, ListView
from nourish.models import Group, EventGroup, GroupUser
from nourish.forms import GroupForm
from django.core.exceptions import PermissionDenied
from pprint import pformat
import sys

from nourish.views.canvas import HybridCanvasView

class GroupDetailView(HybridCanvasView, DetailView):
    context_object_name = 'group'
    model = Group
    template_name='nourish/group_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        context['is_admin'] = self.object.is_admin(self.request.user)
        context['eventgroup_list'] = EventGroup.objects.filter(group=self.object)
    	context['groupuser_list'] = GroupUser.objects.filter(group=self.object)
	try:
	    context['my_membership'] = GroupUser.objects.get(group=self.object,user=self.request.user)
	except GroupUser.DoesNotExist:
	    context['my_membership'] = None
	except TypeError:
	    context['my_membership'] = None
	return context


class GroupUpdateView(HybridCanvasView, UpdateView):
    context_object_name = 'group'
    model = Group
    form_class = GroupForm
    login_required = True

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not self.get_object().is_admin(self.request.user):
            raise PermissionDenied
        return super(GroupUpdateView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated() and not self.get_object().is_admin(self.request.user):
            raise PermissionDenied
        return super(GroupUpdateView, self).post(request, *args, **kwargs)

class GroupListView(HybridCanvasView, ListView):
    model=Group
    template_name='nourish/group_list.html'

