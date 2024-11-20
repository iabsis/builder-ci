from django import template
from django.template.loader import get_template

register = template.Library()

@register.inclusion_tag("includes/sidebar/item.html", takes_context=True)
def sidebar_item(context, name, reverse_url, permission=None):
    request = context['request']
    user = request.user
    permission_name = f'view_{name}'

    has_permission = user.has_perm(permission)

    return {
        "name": name,
        "reverse_url": reverse_url,
        "request": context['request'],
        "has_permission": has_permission
        }

