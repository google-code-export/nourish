from django.views.generic import DetailView, CreateView
from nourish.models import Group, EventGroup, GroupUser
from nourish.forms.group import GroupUserForm

class GroupUserView(CreateView):
    context_object_name = 'groupuser'
    form_class = GroupUserForm
    template_name = 'nourish/group/join.html'

class GroupDetailView(DetailView):
    context_object_name = 'group'
    model = Group
    template_name='nourish/group/detail.html'

    def get_context_data(self, **kwargs):
        context = super(GroupDetailView, self).get_context_data(**kwargs)
        context['eventgroup_list'] = EventGroup.objects.filter(group=self.object)
	context['groupuser_list'] = GroupUser.objects.filter(group=self.object)
	try:
	    context['my_membership'] = GroupUser.objects.get(group=self.object,user=self.request.user)
	except GroupUser.DoesNotExist:
	    context['my_membership'] = None
	return context


