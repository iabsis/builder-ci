from django import template
import re
from django.template.loader import get_template

register = template.Library()

@register.filter
def title(content):
    return re.sub(r'([a-z])([A-Z])', r'\1 \2', content).lower().capitalize()
