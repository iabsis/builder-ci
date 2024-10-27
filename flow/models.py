from django.db import models

# Create your models here.

class Method(models.Model):
    container = models.ForeignKey('container.Container', on_delete=models.CASCADE)
    script = models.TextField()
    flow = models.ForeignKey('Flow', on_delete=models.CASCADE)
    priority = models.IntegerField()

    class Meta:
        unique_together = ['flow', 'priority']

class Flow(models.Model):
    name = models.CharField(max_length=40)
    expected_file = models.CharField(max_length=100)