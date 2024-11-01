from django.db import models
from . import validator
from jinja2 import Template

# Create your models here.

class Method(models.Model):
    name = models.CharField(max_length=40)
    container = models.ForeignKey('container.Container', on_delete=models.CASCADE)
    script = models.TextField()
    stop_on_failure = models.BooleanField(default=False)

    def render_script(self, **variables):
        template = Template(self.script)
        return template.render(variables).replace('\r', '')

    def __str__(self):
        return self.name



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