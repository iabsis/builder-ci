from django.template.loader import get_template
from django import template

register = template.Library()

@register.filter
def options(options):
    return list(set(options))
