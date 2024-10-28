import logging
import importlib
import traceback
import json
import regex
import os
import tempfile
from celery import Celery
from django.conf import settings
from django.utils import timezone
from . import models
from io import StringIO
from podman import PodmanClient
from git import Repo

app = Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)

@app.task
def build_trigger(build_request_id):
    build_request = models.BuildRequest.objects.get(pk=build_request_id)
    if build_request.flows.exists():
        for flow in build_request.flows.all():
            build = models.Build.objects.create(
                request=build_request,
                name=build_request.name,
                flow=flow
            )

            build_run.delay(build.pk)
    build_request.save()


@app.task
def build_run(build_id):

    podman_url = settings.PODMAN_URL

    build = models.Build.objects.get(pk=build_id)
    build.status = models.BuildStatus.running
    build.started_at = timezone.now()

    with tempfile.TemporaryDirectory() as tmpdirname:
        logger.info(f'created temporary directory: {tmpdirname}')

        repo = Repo()
        cloned_repo = repo.clone_from(
            build.request.url, os.path.join(tmpdirname, "sources"), depth=1)
        
        # logger.info(cloned_repo.active_branch)

        pattern = regex.compile(build.flow.version_regex)

        sources_path = os.path.join(tmpdirname, "sources")

        with open(os.path.join(sources_path, build.flow.version_file), 'r') as f:
            c = f.read()
            m = regex.match(pattern, c)
            build.version = m.group(1)
        
        logger.info(f"Found version: {build.version}")


        for method in build.flow.method_set.order_by('priority'):
            script_file = os.path.join(sources_path, 'run')
            with open(script_file, '+w') as f:
                f.write(method.script.replace('\r', ''))
            os.chmod(script_file, 0o755)

            with PodmanClient(base_url=podman_url) as client:
                mounts = [{
                    "target": "/build",
                    "read_only": False,
                    "source": tmpdirname,
                    "type": "bind"
                }]

                image = method.container.get_image_name(
                    **build.request.options)

                logger.info(f"Running image: {image}")

                output = client.containers.run(
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
    build.status = models.BuildStatus.success
    build.save()