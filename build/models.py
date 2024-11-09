from django.db import models
from django_celery_results.models import TaskResult
from jinja2 import Template, StrictUndefined
from . import validations

# Create your models here.
class BuildRequestMode(models.TextChoices):
    ONE_TIME = 'ONE_TIME', 'One time'
    NIGHTLY = 'NIGHTLY', 'Nightly'
    ON_TAG = 'ON_TAG', 'On tag'

class BuildRequestStatus(models.TextChoices):
    failed = 'failed', 'Failed'
    success = 'success', 'Success'

class SourceFetchMode(models.TextChoices):
    GIT = 'GIT', 'Git'

class BuildRequest(models.Model):
    name = models.SlugField(max_length=150)
    fetch_method = models.CharField(choices=SourceFetchMode.choices, max_length=50, default=SourceFetchMode.GIT)
    url = models.CharField(max_length=150)
    branch = models.CharField(max_length=50)
    mode = models.CharField(choices=BuildRequestMode.choices, max_length=50, default=BuildRequestMode.ONE_TIME)
    flows = models.ManyToManyField('flow.Flow', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    options = models.JSONField(default=dict, null=True, blank=True, validators=[validations.validate_dict])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-updated_at"]

class Status(models.TextChoices):
    queued = 'queued', 'Queued'
    success = 'success', 'Success'
    failed = 'failed', 'Failed'
    running = 'running', 'Running'
    warning = 'warning', 'Warning'
    duplicate = 'duplicate', 'Duplicate'
    ignored = 'ignored', 'Ignored'

class BuildTask(models.Model):
    description = models.CharField(max_length=50, null=True, blank=True)
    build = models.ForeignKey('Build', on_delete=models.CASCADE)
    flow = models.ForeignKey('flow.Flow', on_delete=models.CASCADE, null=True)
    method = models.ForeignKey('flow.Method', on_delete=models.CASCADE, null=True)
    order = models.IntegerField()
    logs = models.TextField(null=True, blank=True)
    status = models.CharField(
        choices=Status.choices, null=True, blank=True, max_length=10)
    
    def save(self, *args, **kwargs):
        if not self.description and self.method:
            self.description = self.method.description
        super(BuildTask, self).save(*args, **kwargs)

    @property
    def options(self):
        if self.method:
            return self.method.container.default_options | self.build.options

    @property
    def script(self):
        if self.method:
            t = Template(self.method.script, undefined=StrictUndefined)
            return t.render(**self.options).replace('\r', '')

    class Meta:
        ordering = ['order']

class Build(models.Model):
    request = models.ForeignKey('BuildRequest', blank=True, on_delete=models.CASCADE)
    flow = models.ForeignKey('flow.Flow', on_delete=models.CASCADE)
    version = models.CharField(max_length=100, blank=True)
    celery_task = models.ForeignKey(TaskResult, on_delete=models.SET_NULL, blank=True, null=True)
    meta = models.JSONField(default=dict, validators=[validations.validate_dict])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(choices=Status.choices, max_length=10, default=Status.queued)

    def save(self, *args, **kwargs):
        if not self.status:
            if self.celery_task and self.celery_task.status == 'FAILURE':
                self.status = Status.failed
            elif not self.buildtask_set.all().exists():
                self.status = Status.queued
            elif self.buildtask_set.filter(status=Status.running).exists():
                self.status = Status.running
            elif self.buildtask_set.filter(status=Status.failed, method__stop_on_failure=True).exists():
                self.status = Status.failed
            elif self.buildtask_set.filter(status=Status.failed, method__stop_on_failure=False).exists():
                self.status = Status.warning
            else:
                self.status = Status.success
        super(Build, self).save(*args, **kwargs)

    @property
    def options(self) -> dict:
        '''
        Return the options field in addition of
        name, url and branch.
        '''
        options = self.request.options
        options['name'] = self.request.name
        options['url'] = self.request.url
        options['branch'] = self.request.branch
        return options

    @property
    def logs(self):
        logs = ""
        for task in self.buildtask_set.filter(status=Status.failed):
            logs += f"## Tasks ({task.method.name}) {'Optional' if not task.method.stop_on_failure else ''}\n"
            logs += f"{task.logs}\n"
        return logs

    @property
    def name(self):
        return self.request.name

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']