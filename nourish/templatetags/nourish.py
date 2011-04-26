from django import template

register = template.Library()

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
