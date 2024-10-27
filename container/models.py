from django.db import models

# Create your models here.

class Container(models.Model):

    name = models.CharField(max_length=40)
    dockerfile = models.TextField(null=True)

    def __str__(self):
        return self.name