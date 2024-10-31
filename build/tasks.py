import logging
import importlib
import traceback
import json
import container
import regex
import os
import tempfile
from celery import Celery
from django.conf import settings
from django.utils import timezone

import container.models
from . import models
from flow.models import Flow, Task
from io import StringIO
from podman import PodmanClient
from django_celery_results.models import TaskResult
from git import Repo
from celery import shared_task

app = Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)

@app.task
def build_trigger(build_request_id):
    build_request = models.BuildRequest.objects.get(pk=build_request_id)
    if build_request.flows.exists():
        flows = build_request.flows.all()
    else:
        Flow.objects.all()
    for flow in flows:
        build = models.Build.objects.create(
            request=build_request,
            name=build_request.name,
            flow=flow
        )
        build_run.delay(build.pk)

    build_request.save()

@shared_task(bind=True)
def build_run(self, build_id):

    task_id = self.request.id

    podman_url = settings.PODMAN_URL

    build = models.Build.objects.get(pk=build_id)
    build.started_at = timezone.now()
    build.celery_task = TaskResult.objects.get(task_id=task_id)
    build.save()

    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.info(f'created temporary directory: {tmpdirname}')

        repo = Repo()
        cloned_repo = repo.clone_from(
            build.request.url, os.path.join(tmpdirname, "sources"), depth=1)
        
        # logger.info(cloned_repo.active_branch)

        logger.info(f"Regex to use: {build.flow.version_regex}")
        pattern = regex.compile(build.flow.version_regex)

        sources_path = os.path.join(tmpdirname, "sources")

        with open(os.path.join(sources_path, build.flow.version_file), 'r') as f:
            c = f.read()
            logger.debug(f"File content: {c}")
            m = regex.search(pattern, c)
            logger.debug(f"Matched regex: {m}")
            build.version = m.group(1)
        
        logger.info(f"Found version: {build.version}")
        build.save()


        for task in Task.objects.filter(flow=build.flow).order_by('priority'):
            method = task.method
            script_file = os.path.join(sources_path, 'run')
            with open(script_file, '+w') as f:
                f.write(method.render_script(**build.request.computed_options))
            os.chmod(script_file, 0o755)

            with PodmanClient(base_url=podman_url) as client:
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

                image = method.container.get_target_tag(
                    **build.request.computed_options)
                
                if not container.models.BuiltContainer.objects.filter(name=image).exists():
                    logger.info(f"Container {image} doesn't exist, building")
                    container.tasks.build_image(
                        method.container.pk, **build.request.computed_options)


                logger.info(f"Running image: {image}")

                output = client.containers.run(
                    privileged=True,
                    image=image,
                    remove=True,
                    # environment=,
                    stderr=True,
                    mounts=mounts,
                    entrypoint=['/build/sources/run'],
                    working_dir='/build/sources/',
                )


                # logger.info(output.decode())

                build.logs = output.decode()
                #     [json.loads(log.decode()).get('stream') for log in logs])

    build.finished_at = timezone.now()
    build.save()