import sys
from pprint import pformat

class CanvasMiddleware(object):
    def process_request(self, request):
#        sys.stderr.write("got request: " + pformat(request) + "\n")
        pass
    
    def process_template_response(self, request, response):
        if hasattr(request, 'fbcanvas') and request.fbcanvas:
            response.context_data['canvas'] = True
        return response
