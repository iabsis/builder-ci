from django.db import models
from . import validator
from jinja2 import Template

# Create your models here.

class Variable(models.Model):
    name = models.CharField(max_length=40)
    default_value = models.CharField(max_length=50)
    container = models.ForeignKey('Container', on_delete=models.CASCADE)

class Container(models.Model):

    name = models.CharField(max_length=40)
    dockerfile = models.TextField(blank=True, validators=[validator.validate_dockerfile])

    def __str__(self):
        return self.name
    
    def render_dockerfile(self, **variables):
        template = Template(self.dockerfile)
        return template.render(variables)
    
    def get_image_name(self, **variables):
        image_name = variables.get('image')
        tag_name = variables.get('tag')

        name = self.name

        if image_name:
            name += f"-{image_name}"
        if tag_name:
            name += f"-{tag_name}"

        return name

class BuiltContainerStatus(models.TextChoices):
    SUCCESS = 'SUCCESS', 'Success'
    FAILED = 'FAILED', 'Failed'

class BuiltContainer(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hash = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    variables = models.JSONField(blank=True, null=True)
    logs = models.TextField(blank=True, null=True)
    status = models.TextField(choices=BuiltContainerStatus.choices, blank=True)
    container = models.ForeignKey('Container', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
