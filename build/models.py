from django.db import models

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
    fetch_method = models.CharField(choices=SourceFetchMode.choices, max_length=50, default=SourceFetchMode.GIT)
    url = models.CharField(max_length=150)
    branch = models.CharField(max_length=50)
    mode = models.CharField(choices=BuildRequestMode.choices, max_length=50, default=BuildRequestMode.ONE_TIME)

class BuildStatus(models.TextChoices):
    queued = "queued", "Queued"
    duplicate = "duplicate", 'Duplicate'
    failed = 'failed', 'Failed'
    success = 'success', 'Success'
    warning = 'warning', 'Warning'
    running = 'running', 'Running'

class Build(models.Model):
    name = models.CharField(max_length=100)
    request = models.ForeignKey('BuildRequest', blank=True, on_delete=models.CASCADE)
    flow = models.ForeignKey('flow.Flow', on_delete=models.CASCADE)
    version = models.CharField(max_length=100, blank=True)
    status = models.CharField(choices=BuildStatus.choices, max_length=15, default=BuildStatus.queued)
    options = models.JSONField(blank=True, null=True)
    meta = models.JSONField(blank=True, null=True)
    logs = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)