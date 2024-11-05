from django.db import models
from . import validator
from jinja2 import Template, StrictUndefined

# Create your models here.

class Method(models.Model):
    name = models.CharField(max_length=40)
    container = models.ForeignKey('container.Container', on_delete=models.CASCADE)
    script = models.TextField(help_text="Define the Dockerfile content, use {{var}} for automatic replacement for key defined in options. {{name}} can be used for the project name, {{url}} and {{branch}} are replaced by git respective info")
    stop_on_failure = models.BooleanField(default=False)
    secrets = models.ManyToManyField('secret.Secret', blank=True, help_text="Secrets will be exposed as environement variable with same name")

    def render_script(self, build):
        if build:
            options = build.request.computed_options
        else:
            options = {}

        template = Template(self.script, undefined=StrictUndefined)
        return template.render(**options).replace('\r', '')

    def __str__(self):
        return self.name

    @property
    def serialized_secrets(self):
        return {x.name: x.secret for x in self.secrets.all()}

class Task(models.Model):
    flow = models.ForeignKey('Flow', on_delete=models.CASCADE)
    method = models.ForeignKey('Method', on_delete=models.CASCADE)
    priority = models.IntegerField()

    class Meta:
        unique_together = ['flow', 'priority']

class Flow(models.Model):
    name = models.CharField(max_length=40)
    version_file = models.CharField(max_length=100)
    version_regex = models.CharField(max_length=150, help_text="Define regex with one capturing group.", validators=[validator.validate_regex_pattern])

    def __str__(self):
        return self.name