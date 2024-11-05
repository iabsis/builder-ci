from django.db import models
from . import validator, tasks
from build.models import Build
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
    options_are_mandatory = models.BooleanField(default=False, help_text="Define if {{var}} defined in are mandatory in build request, otherwise fallback to default options that must be defined.")

    def clean(self):
        super().clean()
        if self.options_are_mandatory:
            if self.default_options != None:
                raise ValidationError(
                    "Don't define default options if options are mandatory.", code="invalid")
            else:
                return
        if self.default_options == None:
            raise ValidationError(
                'Default option must not be empty and must at least contain empty dictionnary {}.', code="invalid")
        try:
            self.render_dockerfile()
            self.get_target_tag()
        except UndefinedError as e:
            raise ValidationError(
                f'You defined variable, but is missing in default options: {e}', code="invalid")

    def __str__(self):
        return self.name
    
    def merge_options(self, dictionnary):
        options = self.default_options
        for key, value in dictionnary.items():
            options[key] = value
        return options

    def render_dockerfile(self, build: Build=None):
        if build:
            options = build.request.computed_options
        else:
            options = {}

        template = Template(self.dockerfile, undefined=StrictUndefined)
        if self.options_are_mandatory:
            return template.render(**options)
        else:
            return template.render(**self.merge_options(options))
    
    def get_target_tag(self, build: Build=None):

        if build:
            options = build.request.computed_options
        else:
            options = {}
        
        template = Template(self.target_tag, undefined=StrictUndefined)
        if self.options_are_mandatory:
            return template.render(**options)
        else:
            return template.render(**self.merge_options(options))


class Status(models.TextChoices):
    queued = 'queued', 'Queued'
    success = 'success', 'Success'
    failed = 'failed', 'Failed'
    running = 'running', 'Running'
    warning = 'warning', 'Warning'

class BuiltContainer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hash = models.CharField(max_length=64, blank=True)
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