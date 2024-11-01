from django.template.loader import get_template
from django import template

register = template.Library()

@register.filter
def status_badge(status):
    template = get_template("components/badge.html")
    color = 'secondary'
    if status == 'failed':
        color = 'danger'
    if status == 'success':
        color = 'success'
    if status == 'warning':
        color = 'warning'
    if status == 'queued':
        color = 'primary'

    return template.render({"text": status, "color": color})

