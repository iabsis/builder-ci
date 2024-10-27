from django.db import models

# Create your models here.

class Status(models.TextChoices):
    QUEUED = 'QUEUED', 'Queued'
    FAILED = 'FAILED', 'Failed'
    SUCCESS = 'SUCCESS', 'Success'

class Container(models.Model):

    name = models.CharField(max_length=40)
    dockerfile = models.TextField(null=True)
    status = models.CharField(max_length=40, choices=Status.choices, default=Status.QUEUED)

    def __str__(self):
        return self.name