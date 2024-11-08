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
        builtcontainer = get_object_or_404(models.BuiltContainer, pk=kwargs['pk'])
        builtcontainer.status = models.Status.queued
        builtcontainer.save()
        options = builtcontainer.options
        tasks.build_image.delay(builtcontainer.container.pk, options, force=True)
        messages.success(self.request, f"Rebuild container {builtcontainer} triggered successfully")
        return super().get(request, *args)