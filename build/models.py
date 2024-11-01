from django.db import models
from django_celery_results.models import TaskResult

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
    options = models.JSONField(default=dict)

    @property
    def computed_options(self):
        options = self.options
        options['name'] = self.name
        options['url'] = self.url
        options['branch'] = self.branch
        return options

    def __str__(self):
        return self.name


class TaskStatus(models.TextChoices):
    success = 'success', 'Success'
    failed = 'failed', 'Failed'
    running = 'running', 'Running'

class BuildTask(models.Model):
    flow = models.ForeignKey('flow.Flow', on_delete=models.CASCADE)
    method = models.ForeignKey('flow.Method', on_delete=models.CASCADE)
    order = models.IntegerField()
    logs = models.TextField(null=True, blank=True)
    status = models.CharField(
        choices=TaskStatus.choices, null=True, blank=True, max_length=10)

    class Meta:
        unique_together = ['flow', 'order']

class Build(models.Model):
    request = models.ForeignKey('BuildRequest', blank=True, on_delete=models.CASCADE)
    flow = models.ForeignKey('flow.Flow', on_delete=models.CASCADE)
    version = models.CharField(max_length=100, blank=True)
    celery_task = models.ForeignKey(TaskResult, on_delete=models.DO_NOTHING, blank=True, null=True)
    tasks = models.ManyToManyField(BuildTask, blank=True)
    meta = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    @property
    def name(self):
        return self.request.name

    def __str__(self):
        return self.name
