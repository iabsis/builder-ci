from django.db import models
from . import validator
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
            builtcontainer = BuiltContainer(
                container=self,
                options=self.default_options
            )
            builtcontainer.dockerfile
        except UndefinedError as e:
            raise ValidationError(
                f'You defined variable, but is missing in default options: {e}', code="invalid")

    def __str__(self):
        return self.name

class Status(models.TextChoices):
    queued = 'queued', 'Queued'
    success = 'success', 'Success'
    failed = 'failed', 'Failed'
    running = 'running', 'Running'
    warning = 'warning', 'Warning'

class BuiltContainer(models.Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self._name

    name = models.CharField(max_length=100, unique=True)
    hash = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    logs = models.TextField(blank=True, null=True)
    status = models.TextField(choices=Status.choices, blank=True)
    options = models.JSONField(default=dict, null=True, blank=True)
    container = models.ForeignKey('Container', on_delete=models.CASCADE)

    @property
    def dockerfile(self):
        options = self.container.default_options | self.options
        t = Template(self.container.dockerfile, undefined=StrictUndefined)
        return t.render(**options).replace('\r', '')

    @property
    def _name(self):
        options = self.container.default_options | self.options
        t = Template(self.container.target_tag, undefined=StrictUndefined)
        return t.render(**options).replace('\r', '')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updated_at']