import regex
from django.db import models
from . import validator
from django.forms import ValidationError

# Create your models here.

class Method(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=50, null=True, blank=True)
    container = models.ForeignKey('container.Container', on_delete=models.CASCADE)
    script = models.TextField(help_text="Define the Dockerfile content, use {{var}} for automatic replacement for key defined in options. {{name}} can be used for the project name, {{url}} and {{branch}} are replaced by git respective info")
    stop_on_failure = models.BooleanField(default=True)
    secrets = models.ManyToManyField('secret.Secret', blank=True, help_text="Secrets will be exposed as environement variable with same name")

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
    version_file = models.CharField(max_length=100, null=True, blank=True)
    version_regex = models.CharField(max_length=150, null=True, blank=True, help_text="Define regex with one capturing group.", validators=[validator.validate_regex_pattern])
    version_mandatory = models.BooleanField(default=True, help_text="Define if build failes if version is not found")

    def get_version(self, content):
        pattern = regex.compile(self.version_regex)
        m = regex.search(pattern, content)
        if not m:
            raise Exception("Regex didn't matched anything")
        return m.group(1)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['pk']

    def clean(self):
        super().clean()
        if self.version_mandatory:
            if not self.version_file or not self.version_regex:
                raise ValidationError(
                    "When version is mandatory, you must define Version file and Version Regex", code="invalid")