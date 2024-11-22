from django.db import models
from django_celery_results.models import TaskResult
from jinja2 import Template, StrictUndefined
from . import validations
from django.utils import timezone
from tempfile import TemporaryDirectory
from django.contrib.postgres.fields import ArrayField
from django.forms import ValidationError
from .notification import send_notification

# Create your models here.
class BuildRequestMode(models.TextChoices):
    ON_VERSION = 'ON_VERSION', 'On new version'
    # NIGHTLY = 'NIGHTLY', 'Nightly'
    ON_TAG = 'ON_TAG', 'On new tag'

class BuildRequestStatus(models.TextChoices):
    failed = 'failed', 'Failed'
    success = 'success', 'Success'

class SourceFetchMode(models.TextChoices):
    GIT = 'GIT', 'Git'

class BuildRequest(models.Model):
    name = models.SlugField(max_length=150)
    fetch_method = models.CharField(choices=SourceFetchMode.choices, max_length=50, default=SourceFetchMode.GIT)
    url = models.CharField(max_length=150)
    refname = models.CharField(max_length=50)
    modes = ArrayField(models.CharField(choices=BuildRequestMode.choices, max_length=50), default=list, help_text="Coma separated values", null=True, blank=True)
    flows = models.ManyToManyField('flow.Flow', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    options = models.JSONField(default=dict, null=True, blank=True, validators=[validations.validate_dict])
    requested_by = models.SlugField(max_length=50, null=True, blank=True)

    @property
    def branch(self):
        if self.is_tag:
            return self.refname.replace('refs/tags/', '')
        return self.refname.replace('refs/heads/', '')

    @property
    def is_tag(self):
        if 'tags' in self.refname:
            return True
        return False

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-updated_at"]

    def clean(self):
        super().clean()
        if BuildRequestMode.ON_TAG not in self.modes and self.is_tag:
            raise ValidationError(
                "Build request not accepted with tag but not build ON_TAG", code="invalid")

    def save(self, *args, **kwargs):
        if not self.options:
            self.options = {}
        super(BuildRequest, self).save(*args, **kwargs)

class Status(models.TextChoices):
    queued = 'queued', 'Queued'
    success = 'success', 'Success'
    failed = 'failed', 'Failed'
    running = 'running', 'Running'
    warning = 'warning', 'Warning'
    duplicate = 'duplicate', 'Duplicate'
    ignored = 'ignored', 'Ignored'

class BuildTask(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
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

    def save(self, notify=True, *args, **kwargs):
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
        if notify:
            send_notification(self)
        super(Build, self).save(*args, **kwargs)

    @property
    def tmpfolder(self):
        try:
            return self._tmpfolder
        except:
            self._tmpfolder = SaveBuild(self)
        return self._tmpfolder

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
        options['version'] = self.version
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

    @property
    def build_duration(self):
        if self.finished_at and self.started_at:
            return self.finished_at - self.started_at

    @property
    def eta_total(self):
        try:
            build = Build.objects.filter(
                request__name=self.request.name,
                status=Status.success,
                flow=self.flow
            ).latest('pk')
        except Build.DoesNotExist:
            return
        
        return build.finished_at - build.started_at
    
    @property
    def eta_at(self):
        if self.eta_total:
            print(self.eta_total)
            return self.started_at + self.eta_total

    @property
    def time_elapsed(self):
        return timezone.now() - self.started_at

    @property
    def progress(self):
        if self.eta_total:
            eta_total = round(self.time_elapsed / self.eta_total * 100, -1)
            if eta_total > 100:
                return 100
            return eta_total


class SaveBuild(TemporaryDirectory):
    """
    A class used to store build source code in a temporary directory,
    destroyed in same time than build encountered a fatal error or
    just finished.
    
    Attributes
    ----------
    build : Build
        the build object where source code will stored
    """
    def __init__(self, build: Build, *args, **kargs):
        self.build = build
        super().__init__(*args, **kargs)
        
    def __exit__(self, exc, value, tb):
        if exc is not None:
            if self.build.status == Status.running:
                self.build.status = Status.failed
        if self.build.status == Status.running:
            self.build.status = Status.success
        self.build.save()
        return super().__exit__(exc, value, tb)
    
