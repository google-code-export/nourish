from django import template
from django.db import models
import sys
import re

register = template.Library()

from django.templatetags.future import url

@register.inclusion_tag('nourish/user_link.html')
def userlink(user):
    profile = user.get_profile()
    url = profile.url
    name = profile.fullname

    if not url:
        url = '/users/' + str(user.id)
    if not name:
        name = user.username

    return { 'name' : name, 'url' : url }

class Link(template.Node):
    def __init__(self, urlnode):
        self.urlnode = urlnode

    def render(self, context):
        u = self.urlnode.render(context)
        if 'canvas' in context and context['canvas']:
            p = re.compile("\/nourish\/")
            return p.sub('/nourish/fb/', u)
        else:
            return u

class ObjectLink(template.Node):
    def __init__(self, var):
        self.var = var

    def render(self, context):
        u = self.var.resolve(context).get_absolute_url()
        if 'canvas' in context and context['canvas']:
            p = re.compile("\/nourish\/")
            return p.sub('/nourish/fb/', u)
        else:
            return u

@register.tag(name='nurl')
def clink_tag(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    tp = parser.compile_filter(bits[1])
    p = re.compile("^'")
    if p.match(bits[1]):
        u = url(parser, token)
        return Link(u)
    else:
        return ObjectLink(tp)

