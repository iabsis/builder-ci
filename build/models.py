from django.db import models

# Create your models here.

# class StepType(models.TextChoices):
#     sources = "sources", 'sources'
#     options = "options", 'options'
#     publish = "publish", 'publish'
#     builder = "builder", 'builder'

# class Step(models.Model):
#     build = models.ForeignKey('Build', on_delete=models.CASCADE)
#     method = models.CharField(max_length=15)
#     options = models.JSONField()
#     type = models.CharField(choices=StepType.choices, max_length=15)

#     class Meta:
#         abstract = True

class BuildStatus(models.TextChoices):
    queued = "queued", "Queued"
    duplicate = "duplicate", 'Duplicate'
    failed = 'failed', 'Failed'
    success = 'success', 'Success'
    warning = 'warning', 'Warning'
    running = 'running', 'Running'

class Build(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=100, blank=True)
    status = models.CharField(choices=BuildStatus.choices, max_length=15, default=BuildStatus.queued)
    options = models.JSONField(blank=True, null=True)
    meta = models.JSONField(blank=True, null=True)
    logs = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# class BuildImage(models.Model):
#     name = models.CharField(max_length=100, unique=True)
#     rules = models.TextField()
#     method = models.CharField(max_length=15)
#     type = models.CharField(choices=StepType.choices, max_length=15)
#     meta = models.JSONField()
#     logs = models.JSONField()
