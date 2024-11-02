import logging
import container
import regex
import os
import tempfile
import requests
from celery import Celery
from django.conf import settings
from django.utils import timezone

import container.models
from . import models
from flow.models import Flow, Task
from io import StringIO
from podman import PodmanClient
from podman.errors import ContainerError
from django_celery_results.models import TaskResult
from git import Repo
from celery import shared_task

app = Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)

def send_notification(build):
    
    # TODO : make configurable notification

    if build.status == models.Status.queued:
        status = 'New'
    if build.status == models.Status.failed:
        status = 'Failed'
    if build.status == models.Status.success:
        status = 'Success'
    if build.status == models.Status.running:
        status = 'Running'
    if build.status == models.Status.warning:
        status = 'New'
    if build.status == models.Status.duplicate:
        status = 'Duplicate'

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
                "builder": build.flow.name
            }
        }

        if build.started_at:
            req["json"]["started_at"] = build.started_at.strftime("%Y-%m-%d_%H:%M:%S")
        if build.started_at:
            req["json"]["finished_at"] = build.finished_at.strftime("%Y-%m-%d_%H:%M:%S")


        redmine_id = build.meta.get('redmine_id')
        req['url'] = f"{settings.REDMINE_URL}/builds/{redmine_id}.json" if redmine_id else f"{settings.REDMINE_URL}/builds/new.json"

        response = requests.post(**req)
        response.raise_for_status()

@app.task
def build_request(build_request_id):
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

@shared_task(bind=True)
def build_run(self, build_id):

    # Remove all previous built tasks if existing
    build = models.Build.objects.get(pk=build_id)
    for task in build.tasks.all():
        task.delete()
    build.started_at = timezone.now()

    # Get the current task ID and attach to the requested Build
    build.celery_task = TaskResult.objects.get(task_id=self.request.id)
    build.save()

    # Execute everything in a temporary folder
    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.info(f'created temporary directory: {tmpdirname}')

        # TODO: add support for other source
        repo = Repo()
        cloned_repo = repo.clone_from(
            build.request.url, os.path.join(tmpdirname, "sources"), depth=1)
        
        build.meta['commit_id'] = cloned_repo.head.object.hexsha
        
        # logger.info(cloned_repo.active_branch)


        ### VERSION FETCHING ##
        logger.info(f"Regex to use: {build.flow.version_regex}")
        pattern = regex.compile(build.flow.version_regex)

        sources_path = os.path.join(tmpdirname, "sources")
        version_file = os.path.join(sources_path, build.flow.version_file)

        with open(version_file, 'r') as f:
            c = f.read()
            logger.debug(f"File content: {c}")
            m = regex.search(pattern, c)
            logger.debug(f"Matched regex: {m}")
            build.version = m.group(1)

        logger.info(f"Found version: {build.version}")
        build.save()

        ### TASKS RUNNING ##
        for task in Task.objects.filter(flow=build.flow).order_by('priority'):

            try:
                send_notification(build)
            except Exception as e:
                logger.warning(f"Unable to send notify: {e}")


            build_task = models.BuildTask(
                flow=task.flow,
                method=task.method,
                order=task.priority,
                status=models.Status.running
            )

            build_task.save()
            build.tasks.add(build_task)

            # Create executable script and make it executable
            script_file = os.path.join(sources_path, 'run')
            with open(script_file, '+w') as f:
                f.write(build_task.method.render_script(
                    **build.request.computed_options))
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
                        "source": '/run/user/1000/podman/podman.sock',
                        "type": "bind"
                    }
                ]

                image = build_task.method.container.get_target_tag(
                    **build.request.computed_options)
                
                if not container.models.BuiltContainer.objects.filter(name=image).exists():
                    logger.info(f"Container {image} doesn't exist, building")
                    ## TODO: add try here in event build failes and catch logs
                    container.tasks.build_image(
                        build_task.method.container.pk, **build.request.computed_options)

                logger.info(f"Running image: {image}")
                
                try:
                    output = client.containers.run(
                        privileged=True,
                        image=image,
                        remove=True,
                        environment=task.method.serialized_secrets,
                        stderr=True,
                        mounts=mounts,
                        entrypoint=['/build/sources/run'],
                        working_dir='/build/sources/',
                    )
                    build_task.logs = output.decode()
                    build_task.status = models.Status.success
                    build_task.save()
                except ContainerError as e:
                    build_task.logs = "".join([line.decode() for line in e.stderr])
                    build_task.status = models.Status.failed
                    build_task.save()
                    if build_task.method.stop_on_failure:
                        break

    build.finished_at = timezone.now()
    build.save()