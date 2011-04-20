from django.views.generic import DetailView, CreateView, FormView
from nourish.models import Group, EventGroup, GroupUser
from django.shortcuts import get_object_or_404, redirect
#from nourish.forms.group import GroupUserForm

class GroupJoinView(DetailView):
    context_object_name = 'groupjoin'
    model = Group
    template_name = 'nourish/group/join.html'

    def get_context_data(self, **kwargs):
        context = super(GroupJoinView, self).get_context_data(**kwargs)
        return context

    def post(self,request,pk=None):
	if 'confirm' not in request.POST:
            return self.get(request,pk=pk)

        group = get_object_or_404(Group, pk=pk)
	try:
	    m = GroupUser.objects.get(group=group,user=self.request.user)
	except GroupUser.DoesNotExist:
            m = None

        if m:
            return redirect(group)

        m = GroupUser(group=group,user=request.user)
        m.save()
        return redirect(group)

class GroupLeaveView(DetailView):
    context_object_name = 'groupleave'
    model = Group
    template_name = 'nourish/group/leave.html'

    def get_context_data(self, **kwargs):
        context = super(GroupLeaveView, self).get_context_data(**kwargs)
        return context

    def post(self,request,pk=None):
	if 'confirm' not in request.POST:
            return self.get(request,pk=pk)

        group = get_object_or_404(Group, pk=pk)
	try:
	    m = GroupUser.objects.get(group=group,user=self.request.user)
	except GroupUser.DoesNotExist:
	    context['my_membership'] = None

        if not m.pk:
            return redirect(group)

        m.delete()

        return redirect(group)

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


