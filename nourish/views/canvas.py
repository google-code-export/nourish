import re

class HybridCanvasView(object):
    def get(self, request, **kwargs):
        if 'canvas' in kwargs:
            setattr(self, 'canvas', True)
        return super(HybridCanvasView, self).get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(HybridCanvasView, self).get_context_data(**kwargs)
        if hasattr(self,'canvas'):
            context['canvas'] = self.canvas
        return context


rewriter_re = re.compile("\/nourish\/")

def canvas_url_rewrite(url):
    return rewriter_re.sub('/nourish/fb/', u)
