from django.contrib import admin
from . import models

# Register your models here.

admin.site.register(models.Build)
admin.site.register(models.BuildRequest)