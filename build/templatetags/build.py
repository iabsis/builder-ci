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


@register.filter
def view_field(list_field):
    if isinstance(list_field, list):
        template = get_template("components/badge.html")
        rendered_output = "".join(
            [template.render({"text": item, "color": "primary"}) for item in list_field]
        )
        return rendered_output
    return list_field