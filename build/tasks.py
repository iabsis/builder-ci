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
        build_run.delay(build.pk)

    build_request.save()


@app.task(bind=True, time_limit=900)
def build_run(self, build_id):

    # Remove all previous built tasks if existing
    build = models.Build.objects.get(pk=build_id)
    for task in build.buildtask_set.all():
        task.delete()
    build.started_at = timezone.now()
    build.status = models.Status.running

    # Get the current task ID and attach to the requested Build
    build.celery_task = TaskResult.objects.get(task_id=self.request.id)
    build.save()

    # Execute everything in a temporary folder
    with build.tmpfolder as tmpdirname:
        
        with BuildTaskExecutor(build, "Cloning repository") as task:
            actions.clone_repository(task, tmpdirname)
        
        # logger.info(cloned_repo.active_branch)

        ### VERSION FETCHING ##
        with BuildTaskExecutor(build, "Version fetching") as task:
            actions.fetch_version(task, tmpdirname)

        build.save()

        ### DUPLICATES CHECK ##
        with BuildTaskExecutor(build, "Duplicates check") as task:
            actions.duplicates_check(task, tmpdirname)

        ### TASKS DEFINITION ##
        for task in Task.objects.filter(flow=build.flow).order_by('priority'):

            image_task = models.BuildTask.objects.create(
                build=build,
                description="Check for container sanity or construct",
                status=models.Status.queued
            )

            build_task = models.BuildTask.objects.create(
                build=build,
                flow=task.flow,
                method=task.method,
                status=models.Status.queued,
                image_task=image_task
            )

        ### TASKS RUNNING ##
        for build_task in models.BuildTask.objects.filter(build=build, flow__isnull=False).order_by('order'):

            send_notification(build)

            with BuildTaskExecutor(buildtask=build_task.image_task) as task:
                builtcontainer_name = actions.build_container_image(build_task.image_task, tmpdirname)
    
            with BuildTaskExecutor(buildtask=build_task) as task:
                actions.build_action(task, builtcontainer_name, tmpdirname)
                

    # Set to None will automatically detect the status
    build.status = models.Status.success
    build.finished_at = timezone.now()
    build.save()
    send_notification(build)