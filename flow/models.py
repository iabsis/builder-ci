import re
from django.db import models
from . import validator
from django.forms import ValidationError
from jinja2 import Environment, meta
from git import repo

# Create your models here.

class Method(models.Model):
    name = models.CharField(max_length=40)
    description = models.CharField(max_length=100, null=True, blank=True)
    container = models.ForeignKey('container.Container', on_delete=models.CASCADE)
    script = models.TextField(help_text="Define the Dockerfile content, use {{var}} for automatic replacement for key defined in options. {{name}} can be used for the project name, {{url}} and {{branch}} are replaced by git respective info")
    stop_on_failure = models.BooleanField(default=True)
    secrets = models.ManyToManyField('secret.Secret', blank=True, help_text="Secrets will be exposed as environement variable with same name")

    def __str__(self):
        return self.name

    @property
    def options(self):
        env = Environment()
        parsed_content = env.parse(self.script)
        undeclared_variables = meta.find_undeclared_variables(parsed_content)
        for var in ['name', 'url', 'branch', 'version']:
            if var in undeclared_variables:
                undeclared_variables.remove(var)
        return [k for k in undeclared_variables] + self.container.options

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
    description = models.CharField(max_length=100, null=True, blank=True)
    version_file = models.CharField(max_length=100, null=True, blank=True)
    version_regex = models.CharField(max_length=150, null=True, blank=True, help_text="Define regex with one capturing group.", validators=[validator.validate_regex_pattern])
    version_mandatory = models.BooleanField(default=True, help_text="Define if build failes if version is not found")

    @property
    def options(self):
        options = []
        for task in self.task_set.all():
            options += task.method.options
        for var in ['name', 'url', 'branch', 'version']:
            if var in options:
                options.remove(var)
        return options

    def get_version_content(self, version_content):
        '''Get version from string content'''
        pattern = re.compile(self.version_regex)
        m = re.search(pattern, version_content)
        if not m:
            raise Exception("Regex didn't matched anything")
        return m.group(1)

    def get_version(self, version_file):
        '''Get version from file'''
        with open(version_file, 'r') as f:
            content = f.read()
            pattern = re.compile(self.version_regex)
            m = re.search(pattern, content)
            if not m:
                raise Exception("Regex didn't matched anything")
            return m.group(1)

    def gen_version(self, version_file):
        '''Gen version using git describe --tags'''
        new_version = repo.Repo("./").git.describe('--tags')
        return self.replace_version(version_file, new_version)

    def replace_version(self, version_file, new_version):
        with open(version_file, 'r') as f:
            content = f.read()

        pattern = re.compile(self.version_regex)

        def replace_group_1(match):
            return match.group(0).replace(match.group(1), new_version)
    
        updated_content = re.sub(pattern, replace_group_1, content, count=1)

        with open(version_file, 'w') as f:
            f.write(updated_content)
        
        return self.get_version(version_file)

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