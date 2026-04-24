from django.views.generic import DetailView
from django.views.generic import RedirectView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from . import models, tasks
from django.http import HttpResponseRedirect
from sbadmin2.permission import DynamicPermissionMixin
from sbadmin2.views import GenericViewList
from django.db.models import Q, F
from django.utils import timezone
from celery import current_app
from podman import PodmanClient
from django.conf import settings

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

class StopBuildView(LoginRequiredMixin, RedirectView):
    pattern_name = 'build'

    def get(self, request, *args, **kwargs):
        build = get_object_or_404(models.Build, pk=kwargs['pk'])
        if build.status == models.Status.running:
            # Stop any running Podman containers for this build
            try:
                with PodmanClient(base_url=settings.PODMAN_URL) as client:
                    for c in client.containers.list(filters={"label": f"builder_ci_build_id={build.pk}"}):
                        c.stop(timeout=2)
                        c.remove()
            except Exception:
                pass

            # Revoke the Celery task
            if build.celery_task:
                current_app.control.revoke(
                    build.celery_task.task_id, terminate=True, signal='SIGTERM')

            build.status = models.Status.failed
            build.finished_at = timezone.now()
            build.save()
            messages.success(self.request, f"Build {build.name} stopped")

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


class BuildListView(GenericViewList):
    model = models.Build
    show_filter = False

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(request__name__icontains=search)
        return queryset


class BuildTablePartial(LoginRequiredMixin, ListView):
    model = models.Build
    template_name = 'build/partial/build_table.html'
    paginate_by = 10
    context_object_name = 'object_list'

    def get_queryset(self):
        queryset = models.Build.objects.all().order_by(F('started_at').desc(nulls_first=True), '-created_at')
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(request__name__icontains=search)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['view_url'] = 'build_view'
        return context
