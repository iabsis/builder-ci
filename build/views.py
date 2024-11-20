from django.views import View
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from . import models, tasks
from django.http import HttpResponseRedirect
from sbadmin2.permission import DynamicPermissionMixin

# Create your views here.

class RunBuildView(LoginRequiredMixin, RedirectView):
    pattern_name = 'build'

    def get(self, request, *args, **kwargs):
        build = get_object_or_404(models.Build, pk=kwargs['pk'])
        build.status = models.Status.queued
        build.save()
        for task in build.buildtask_set.all():
            task.delete()
        if build.celery_task:
            build.celery_task.delete()
        tasks.build_run.delay(build.pk)
        messages.success(self.request, f"Build {build.name} triggered successfully")
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        return super().get(request, *args)

class TriggerBuildRequestView(LoginRequiredMixin, RedirectView):
    pattern_name = 'request'

    def get(self, request, *args, **kwargs):
        buildrequest = get_object_or_404(models.BuildRequest, pk=kwargs['pk'])
        tasks.build_request.delay(buildrequest.pk)
        messages.success(
            self.request, f"Build {buildrequest.name} triggered successfully")
        return super().get(buildrequest, *args)
