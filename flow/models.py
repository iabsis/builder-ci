from django.db import models
from . import validator

# Create your models here.

class Method(models.Model):
    name = models.CharField(max_length=40)
    container = models.ForeignKey('container.Container', on_delete=models.CASCADE)
    script = models.TextField()
    flow = models.ForeignKey('Flow', on_delete=models.CASCADE)
    stop_on_failure = models.BooleanField(default=False)
    priority = models.IntegerField()

    class Meta:
        unique_together = ['flow', 'priority']

    def __str__(self):
        return self.name

class Flow(models.Model):
    name = models.CharField(max_length=40)
    version_file = models.CharField(max_length=100)
    version_regex = models.CharField(max_length=150, help_text="Define regex with one capturing group.", validators=[validator.validate_regex_pattern])

    def __str__(self):
        return self.name