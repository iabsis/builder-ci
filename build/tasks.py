import logging
import container
import os
import celery
from django.utils import timezone
import container.models
from . import models, actions
from flow.models import Flow, Task
from django_celery_results.models import TaskResult
from django.conf import settings
from .executor import BuildTaskExecutor
from .notification import send_notification

app = celery.Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)

@app.task(bind=True)
def build_request(self, build_request_id):
    build_request = models.BuildRequest.objects.get(pk=build_request_id)
    if build_request.flows.exists():
        flows = build_request.flows.all()
    else:
        flows = Flow.objects.all()
    for flow in flows:
        build = models.Build.objects.create(
            request=build_request,
            flow=flow
        )
        create_tasks(build.pk)
        build_run.delay(build.pk)

    build_request.save()

@app.task
def create_tasks(build_id):
    build = models.Build.objects.get(pk=build_id)
    for task in build.buildtask_set.all():
        task.delete()
    build.status = models.Status.queued
    send_notification(build)

    models.BuildTask.objects.create(
        build=build,
        description="Cloning repository",
        status=models.Status.queued,
        action="clone_repository"
    )

    models.BuildTask.objects.create(
        build=build,
        description="Version fetching",
        status=models.Status.queued,
        action="fetch_version"
    )

    models.BuildTask.objects.create(
        build=build,
        description="Duplicates check",
        status=models.Status.queued,
        action="duplicates_check"
    )

    for task in Task.objects.filter(flow=build.flow).order_by('priority'):

        image_task = models.BuildTask.objects.create(
            build=build,
            description="Check for container sanity or construct",
            status=models.Status.queued
        )

        models.BuildTask.objects.create(
            build=build,
            flow=task.flow,
            method=task.method,
            status=models.Status.queued,
            image_task=image_task
        )

@app.task(bind=True, time_limit=900)
def build_run(self, build_id):
    build = models.Build.objects.get(pk=build_id)
    build.started_at = timezone.now()
    build.status = models.Status.running
    send_notification(build)

    # Get the current task ID and attach to the requested Build
    build.celery_task = TaskResult.objects.get(task_id=self.request.id)
    build.save()

    # Execute everything in a temporary folder
    with build.tmpfolder as tmpdirname:
        for build_task in models.BuildTask.objects.filter(
                                    build=build, status=models.Status.queued
                                ).order_by('order'):
            
            logger.info(f"Running: {build_task}")

            if build_task.action:
                with BuildTaskExecutor(buildtask=build_task) as task_executor:
                    func = getattr(actions, build_task.action)
                    func(task_executor, tmpdirname)
                    continue
            
            if build_task.image_task:
                with BuildTaskExecutor(buildtask=build_task) as task_executor:
                    actions.build_action(task_executor, tmpdirname)
                continue

            logger.debug(f"Task: {build_task}")
            with BuildTaskExecutor(buildtask=build_task) as task_executor:
                build_task.image_name = actions.build_container_image(task_executor, tmpdirname)
                build_task.save()

    build.refresh_from_db()
    build.status = models.Status.success
    build.finished_at = timezone.now()
    build.save()
    send_notification(build)
        
