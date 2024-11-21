from django.template.loader import get_template
from django import template
from django.template.defaultfilters import linebreaks_filter
from ..models import Status
import yaml

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
def view_field(field_content):
    if field_content == '':
        return None
    if isinstance(field_content, str):
        return linebreaks_filter(field_content)
    if isinstance(field_content, dict):
        if field_content == {}:
            return None
        template = get_template("components/pre.html")
        yaml_data = yaml.dump(field_content)
        return template.render({"code": yaml_data})
    if isinstance(field_content, list):
        template = get_template("components/badge.html")
        rendered_output = "".join(
            [template.render({"text": item, "color": "primary"}) for item in field_content]
        )
        return rendered_output
    return field_content