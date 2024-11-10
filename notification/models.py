from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MatrixInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    room_id = models.CharField(max_length=20, null=True, blank=True)
