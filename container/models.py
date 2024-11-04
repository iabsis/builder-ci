from django.db import models
from . import validator, tasks
from django.forms import ValidationError
from jinja2 import Template, StrictUndefined, UndefinedError

# Create your models here.

class Variable(models.Model):
    name = models.CharField(max_length=40)
    default_value = models.CharField(max_length=50)
    container = models.ForeignKey('Container', on_delete=models.CASCADE)

class Container(models.Model):

    name = models.SlugField(max_length=40)
    dockerfile = models.TextField(blank=True, validators=[validator.validate_dockerfile], help_text="Define the Dockerfile content, use {{var}} for automatic replacement for key defined in options.")
    target_tag = models.CharField(max_length=50, default='builder-{{image}}-{{tag}}')
    default_options = models.JSONField(default=dict, null=True, blank=True)

    def clean(self):
        if self.default_options == None:
            raise ValidationError(
                'Default option must not be empty and must at least contain empty dictionnary {}.', code="invalid")
        try:
            self.render_dockerfile(**self.default_options)
            self.get_target_tag(**self.default_options)
        except UndefinedError as e:
            raise ValidationError(
                f'You defined variable, but is missing in default options: {e}', code="invalid")

        super().clean()

    def __str__(self):
        return self.name
    
    def render_dockerfile(self, **variables):
        template = Template(self.dockerfile, undefined=StrictUndefined)
        return template.render(variables)
    
    def get_target_tag(self, **variables):
        template = Template(self.target_tag, undefined=StrictUndefined)
        return template.render(variables)


class Status(models.TextChoices):
    queued = 'queued', 'Queued'
    success = 'success', 'Success'
    failed = 'failed', 'Failed'
    running = 'running', 'Running'
    warning = 'warning', 'Warning'

class BuiltContainer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hash = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    variables = models.JSONField(blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    status = models.TextField(choices=Status.choices, blank=True)
    container = models.ForeignKey('Container', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at']