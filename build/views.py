from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from . import models, tasks
from django.http import HttpResponseRedirect
from sbadmin2.permission import DynamicPermissionMixin
from sbadmin2.views import GenericViewList
from django.db.models import Q

# Create your views here.

class RunBuildView(LoginRequiredMixin, RedirectView):
    pattern_name = 'build'

    def get(self, request, *args, **kwargs):
        build = get_object_or_404(models.Build, pk=kwargs['pk'])
        tasks.create_tasks(build.pk)
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
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        return super().get(buildrequest, *args)


class TriggerBuildInfoPartial(LoginRequiredMixin, DetailView):
    model = models.Build
    template_name = 'build/partial/info.html'


class BuildRequestListView(GenericViewList):
    model = models.BuildRequest
    show_filter = False

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset
