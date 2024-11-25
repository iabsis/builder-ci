from django import template
from django.template.loader import get_template

register = template.Library()

@register.inclusion_tag("includes/sidebar/item.html", takes_context=True)
def sidebar_item(context, name, reverse_url, permission=None):
    request = context['request']
    user = request.user
    has_permission = user.has_perm(permission)

    return {
        "name": name,
        "reverse_url": reverse_url,
        "request": context['request'],
        "has_permission": has_permission
        }

@register.filter
def show_menu(url, menu):
    if menu == 'builds':
        if 'request' in url or 'build' in url or 'builtcontainer' in url:
            return True
    if menu == 'config':
        if 'configcontainer' in url or 'method' in url or 'flow' in url or 'secret' in url:
            return True
    return False
