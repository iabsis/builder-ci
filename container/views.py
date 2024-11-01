from . import models
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from . import models, tasks

class ReBuildContainer(LoginRequiredMixin, RedirectView):
    pattern_name = 'builtcontainer'

    def get(self, request, *args, **kwargs):
        build = get_object_or_404(models.BuiltContainer, pk=kwargs['pk'])
        build.status = models.Status.queued
        tasks.build_image.delay(build.container.pk, **build.variables)
        messages.success(self.request, f"Build {build.name} triggered successfully")
        return super().get(request, *args)