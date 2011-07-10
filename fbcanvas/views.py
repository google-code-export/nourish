from django.views.generic import TemplateView

import re

class HybridCanvasView(object):
    def get(self, request, **kwargs):
        if 'fbcanvas' in kwargs:
            setattr(request, 'fbcanvas', True)
        return super(HybridCanvasView, self).get(request, **kwargs)

    def post(self, request, **kwargs):
        if 'fbcanvas' in kwargs:
            setattr(request, 'fbcanvas', True)
        if hasattr(super(HybridCanvasView, self), 'post'):
            return super(HybridCanvasView, self).post(request, **kwargs)
        return

class CanvasTemplateView(HybridCanvasView, TemplateView):
    pass

rewriter_re = re.compile("\/nourish\/")

def canvas_url_rewrite(url):
    return rewriter_re.sub('/nourish/fb/', u)
