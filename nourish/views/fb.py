from django.shortcuts import render_to_response, redirect
from django.template import RequestContext

def fb(request):
    return render_to_response('nourish/fb.html', { 
        'request': request,
    }, context_instance=RequestContext(request))
