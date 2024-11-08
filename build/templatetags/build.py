from django.template.loader import get_template
from django import template
from ..models import Status

register = template.Library()

@register.filter
def status_badge(status):
    template = get_template("components/badge.html")
    color = 'secondary'
    if status == Status.failed:
        color = 'danger'
    if status == Status.success:
        color = 'success'
    if status in [Status.warning, Status.duplicate]:
        color = 'warning'
    if status == Status.queued:
        color = 'primary'

    return template.render({"text": status, "color": color})

