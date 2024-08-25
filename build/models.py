from django.db import models

# Create your models here.

class StepType(models.TextChoices):
    sources = "sources", 'sources'
    options = "options", 'options'
    publish = "publish", 'publish'
    builder = "builder", 'builder'

class Step(models.Model):
    build = models.ForeignKey('Build', on_delete=models.CASCADE)
    method = models.CharField(max_length=15)
    options = models.JSONField()
    type = models.CharField(choices=StepType.choices, max_length=15)

    class Meta:
        unique_together = ['build', 'method', 'type']

class BuildStatus(models.TextChoices):
    duplicate = "duplicate", 'Duplicate'
    failed = 'failed', 'Failed'
    success = 'success', 'Success'
    running = 'running', 'Running'

class Build(models.Model):
    project = models.CharField(max_length=100)
    status = models.CharField(choices=BuildStatus.choices, max_length=15)
    meta = models.JSONField()
    logs = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)