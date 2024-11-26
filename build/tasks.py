import logging
import container
import os
import celery
from django.utils import timezone
import container.models
from . import models
from flow.models import Flow, Task
from podman import PodmanClient
from podman.errors import ContainerError
from django_celery_results.models import TaskResult
from git import Repo
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
        logger.info(f'created temporary directory: {tmpdirname}')

        with BuildTaskExecutor(build, "Cloning repository") as task:
            cloned_repo = Repo.clone_from(
                build.request.url, os.path.join(tmpdirname, "sources"), depth=1, branch=build.request.branch, single_branch=True)


        build.meta['commit_id'] = cloned_repo.head.object.hexsha
        
        # logger.info(cloned_repo.active_branch)

        ### VERSION FETCHING ##
        try:
            with BuildTaskExecutor(build, "Version fetching") as task:
                version_file = os.path.join(tmpdirname, "sources", build.flow.version_file)
                if models.BuildRequestMode.ON_VERSION in build.request.modes and not build.request.is_tag:
                    logger.info(f"Regex to use: {build.flow.version_regex}")
                    build.version = build.flow.get_version(version_file)

                if models.BuildRequestMode.ON_TAG in build.request.modes and build.request.is_tag:
                    logger.info(f"Regex to use: {build.flow.version_regex}")
                    build.version = build.flow.replace_version(version_file, build.request.branch)
                
                if not build.version and build.flow.version_mandatory:
                    raise Exception("Version is missing while flow requires a version")
        except Exception as e:
            if build.flow.version_mandatory:
                message = f"Version is missing while flow requires a version: {e}"
                raise Exception(message)
            else:
                task.status = models.Status.ignored
                message = f"Version is missing but flow DOESN'T require a version: {e}"
            task.logs = message
            task.save()
        build.save()

        ### DUPLICATES CHECK ##
        with BuildTaskExecutor(build, "Duplicates check") as task:
            if models.Build.objects.filter(
                request__name=build.request.name,
                flow=build.flow,
                version=build.version,
                status=models.Status.success,
            ).exclude(
                version=''
            ).exclude(
                version__isnull=True
            ).exists():
                build.status = models.Status.duplicate
                send_notification(build)
                raise Exception("Same success version found, stopping")


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

            with BuildTaskExecutor(buildtask=build_task.image_task) as _:
                try:
                    builtcontainer_name = container.tasks.build_image(
                        build_task.method.container.pk, build_task.options)
                except Exception as e:
                    logger.debug(e)
                    raise Exception(e)
    
            with BuildTaskExecutor(buildtask=build_task) as task:

                # Create executable script and make it executable
                script_file = os.path.join(tmpdirname, "sources", 'run')
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
                    
                    except ContainerError as e:
                        logger.error(e.stderr)
                        logs = "".join([line.decode() for line in e.stderr])
                        build_task.logs = f"exception occured executing task: {e}, {logs}"
                        build_task.status = models.Status.failed
                        build.save()
                        if build_task.method.stop_on_failure:
                            raise Exception("A mandatory task failed, stopping")
                    except Exception as e:
                        build_task.status = models.Status.failed
                        build_task.logs = f"exception occured executing task: {e}"
                        build.save()
                        if build_task.method.stop_on_failure:
                            raise Exception("A mandatory task failed, stopping")

    # Set to None will automatically detect the status
    build.status = models.Status.success
    build.finished_at = timezone.now()
    build.save()
    send_notification(build)