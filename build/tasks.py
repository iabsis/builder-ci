import logging
import container
import os
import requests
import celery
from django.conf import settings
from django.utils import timezone
import container.models
from . import models
from flow.models import Flow, Task
from podman import PodmanClient
from podman.errors import ContainerError
from django_celery_results.models import TaskResult
from git import Repo
from celery import shared_task
from .executor import BuildTaskExecutor


app = celery.Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)


def send_notification(build):
    
    # TODO : make configurable notification

    if build.status == models.Status.queued:
        status = 'New'
    elif build.status == models.Status.failed:
        status = 'Failed'
    elif build.status == models.Status.success:
        status = 'Success'
    elif build.status == models.Status.running:
        status = 'Running'
    elif build.status == models.Status.warning:
        status = 'New'
    elif build.status == models.Status.duplicate:
        status = 'Duplicate'
    else:
        logger.debug(f"Received unknow status: {build.status}")
        status = 'Failed'

    if settings.REDMINE_KEY and settings.REDMINE_URL:
        req = {
            "headers": {
                'Content-Type': 'application/json',
                'X-Redmine-Api-Key': settings.REDMINE_KEY
            },
            "json": {
                "project": build.name,
                "status": status,
                "release": build.version,
                "commit": build.meta.get('commit_id'),
                "target": 'undefined',
                "builder": build.flow.name,
                "logs": build.logs,
            }
        }

        if build.started_at:
            req["json"]["started_at"] = build.started_at.strftime("%Y-%m-%d_%H:%M:%S") if build.started_at else None
        if build.started_at:
            req["json"]["finished_at"] = build.finished_at.strftime("%Y-%m-%d_%H:%M:%S") if build.finished_at else None


        redmine_id = build.meta.get('redmine_id')
        req['url'] = f"{settings.REDMINE_URL}/builds/{redmine_id}.json" if redmine_id else f"{settings.REDMINE_URL}/builds/new.json"

        response = requests.post(**req)
        if response.status_code != 200:
            logger.error(f"Unable to notify Redmine: {response.text}, {req['json']}")
        # response.raise_for_status()


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


@app.task(bind=True)
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
        logger.info(f'created temporary directory: {tmpdirname}')

        # Stop build if the buildrequest is due to a tag but build is not supposed
        # to build when it's tag.
        with BuildTaskExecutor(build, "Check build sanity") as task:
            if models.BuildRequestMode.ON_TAG not in build.request.modes and build.request.is_tag:
                raise Exception("Not building because this push is not a tag while build mode is ON_TAG")
            if not models.BuildRequestMode.ON_TAG not in build.request.modes and not build.request.is_tag:
                raise Exception(
                    "Not building because this push is not a tag while build mode is ON_TAG")

        with BuildTaskExecutor(build, "Cloning repository") as task:
            cloned_repo = Repo.clone_from(
                build.request.url, os.path.join(tmpdirname, "sources"), depth=1, branch=build.request.branch, single_branch=True)


        build.meta['commit_id'] = cloned_repo.head.object.hexsha
        
        # logger.info(cloned_repo.active_branch)

        ### VERSION FETCHING ##
        with BuildTaskExecutor(build, "Version fetching") as task:
            logger.info(f"Regex to use: {build.flow.version_regex}")

            sources_path = os.path.join(tmpdirname, "sources")
            version_file = os.path.join(sources_path, build.flow.version_file)

            with open(version_file, 'r') as f:
                content = f.read()
                logger.debug(f"File content: {content}")
                build.version = build.flow.get_version(content)

        ### DUPLICATES CHECK ##
        with BuildTaskExecutor(build, "Duplicates check") as task:
            if models.Build.objects.filter(
                request=build.request,
                flow=build.flow,
                version=build.version,
                status=models.Status.success,
            ).exclude(
                version__isnull=True,
                pk=build.pk
            ).exists():
                build.status = models.Status.duplicate
                raise Exception("Same success version found, stopping")


        ### TASKS DEFINITION ##
        for task in Task.objects.filter(flow=build.flow).order_by('priority'):

            build_task = models.BuildTask.objects.create(
                build=build,
                flow=task.flow,
                method=task.method,
                order=task.priority,
                status=models.Status.queued
            )

        ### TASKS RUNNING ##
        for build_task in models.BuildTask.objects.filter(build=build, flow__isnull=False).order_by('order'):

            with BuildTaskExecutor(buildtask=build_task) as task:
            
                send_notification(build)

                # Create executable script and make it executable
                script_file = os.path.join(sources_path, 'run')
                with open(script_file, '+w') as f:
                    f.write(build_task.script)
                os.chmod(script_file, 0o755)

                with PodmanClient(base_url=settings.PODMAN_URL) as client:
                    mounts = [
                        {
                            "target": "/build",
                            "read_only": False,
                            "source": tmpdirname,
                            "type": "bind"
                        },
                        {
                            "target": "/run/podman/podman.sock",
                            "read_only": False,
                            "source": settings.PODMAN_PATH,
                            "type": "bind"
                        }
                    ]

                    try:

                        with BuildTaskExecutor(build, "Check for container sanity or build") as _:
                            builtcontainer_name = container.tasks.build_image(
                                build_task.method.container.pk, build_task.options)

                        output = client.containers.run(
                            privileged=True,
                            image=builtcontainer_name,
                            remove=True,
                            environment=task.method.serialized_secrets,
                            stderr=True,
                            mounts=mounts,
                            network_mode="host",
                            entrypoint=['/build/sources/run'],
                            working_dir='/build/sources/',
                            user='0',
                        )
                        task.logs = output.decode()

                    except Exception as e:
                        build_task.status = models.Status.failed
                        logs = "".join([line.decode() for line in e.stderr])
                        build_task.logs = f"exception occured executing task: {e}\n {logs}"
                        if build_task.method.stop_on_failure:
                            raise Exception("A mandatory task failed, stopping")

    # Set to None will automatically detect the status
    build.status = models.Status.success
    build.finished_at = timezone.now()
    build.save()
    send_notification(build)