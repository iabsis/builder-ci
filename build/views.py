from django.views import View
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from . import models, tasks

# Create your views here.


class RunBuildView(LoginRequiredMixin, RedirectView):
    pattern_name = 'build'

    def get(self, request, *args, **kwargs):
        build = get_object_or_404(models.Build, pk=kwargs['pk'])
        tasks.build_run.delay(build.pk)
        for task in build.tasks.all():
            task.delete()
        messages.success(self.request, f"Build {build.name} triggered successfully")
        return super().get(request, *args)

class Build(View):
    def post(self, request, *args, **kwargs):

        build_request = models.BuildRequest.objects.create(
            name=kwargs.get('name')
        )

        tasks.build_request.delay(build_request.pk)
        JsonResponse({"test": "test"})