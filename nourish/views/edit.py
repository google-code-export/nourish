import django

class CreateView(django.views.generic.CreateView):
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
	form.request = request
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
