from . import models
from .executor import BuildTaskExecutor
import os
import logging
from .notification import send_notification
import container
from podman import PodmanClient
from podman.errors import ContainerError
from django.conf import settings
from git import Repo

logger = logging.getLogger(__name__)

def clone_repository(task_executor: BuildTaskExecutor, builddir):
    task = task_executor.task
    task_executor.add_logs(f"Cloning repository: {task.build.request.url}")
    logger.info(f'created temporary directory: {builddir}')
    cloned_repo = Repo.clone_from(
        task.build.request.url, os.path.join(builddir, "sources"), depth=1, branch=task.build.request.branch, single_branch=True)

    task.build.meta['commit_id'] = cloned_repo.head.object.hexsha

def fetch_version(task_executor: BuildTaskExecutor, builddir):
    task = task_executor.task
    exception = None
    try:
        version_file = os.path.join(builddir, "sources", task.build.flow.version_file)
        if models.BuildRequestMode.ON_VERSION in task.build.request.modes and not task.build.request.is_tag:
            task_executor.add_logs(f"Regex to use (get): {task.build.flow.version_regex}")
            task.build.version = task.build.flow.get_version(version_file)
            task.build.save()
            task_executor.add_logs(f"Got version: {task.build.version}")

        if models.BuildRequestMode.ON_TAG in task.build.request.modes and task.build.request.is_tag:
            task_executor.add_logs(f"Regex to use (replace): {task.build.flow.version_regex}")
            task.build.version = task.build.flow.replace_version(version_file, task.build.request.branch)
            task.build.save()

        if models.BuildRequestMode.ON_COMMIT in task.build.request.modes and not task.build.request.is_tag:
            task_executor.add_logs(f"Regex to use (replace): {task.build.flow.version_regex}")
            task.build.version = task.build.flow.gen_version(version_file)
            task.build.save()
            task_executor.add_logs(f"Generated version: {task.build.version}")

    except Exception as e:
        exception = e
        
    if not task.build.version and task.build.flow.version_mandatory:
        message = f"Version is missing while flow requires a version, {exception}"
        task.logs = message
        task.save()
        raise Exception(message)
        
    if not task.build.version and not task.build.flow.version_mandatory:
        task.status = models.Status.ignored
        message = f"Version is missing but flow DOESN'T require a version: {exception}"
        task.logs = message
        task.save()

def duplicates_check(task_executor: BuildTaskExecutor, builddir):
    task = task_executor.task
    if models.Build.objects.filter(
        request__name=task.build.request.name,
        flow=task.build.flow,
        version=task.build.version,
        status=models.Status.success,
    ).exclude(
        version=''
    ).exclude(
        version__isnull=True
    ).exists():
        task.build.status = models.Status.duplicate
        message = "Same success version found, stopping\n"
        task_executor.add_logs(message)
        send_notification(task.build)
        raise Exception(message)
    message = "No duplicate version\n"
    task.logs = message
    task_executor.add_logs(message)

def build_container_image(task_executor: BuildTaskExecutor, builddir):
    task = task_executor.task
    try:
        return container.tasks.build_image(
            task.buildtask.method.container.pk, task.buildtask.options)
    except Exception as e:
        logger.debug(e)
        raise Exception(e)

def build_action(task_executor: BuildTaskExecutor, builddir):
    task = task_executor.task
    # Create script and make it executable
    script_file = os.path.join(builddir, "sources", 'run')
    with open(script_file, '+w') as f:
        f.write(task.script)
    os.chmod(script_file, 0o755)


    with PodmanClient(base_url=settings.PODMAN_URL) as client:
        mounts = [
            {
                "target": "/build",
                "read_only": False,
                "source": builddir,
                "type": "bind"
            },
            {
                "target": "/run/podman/podman.sock",
                "read_only": False,
                "source": settings.PODMAN_PATH,
                "type": "bind"
            }
        ]

        container_output = client.containers.run(
            privileged=True,
            image=task.image_task.image_name,
            environment=task.method.serialized_secrets,
            stderr=True,
            mounts=mounts,
            network_mode="host",
            entrypoint=['/build/sources/run'],
            working_dir='/build/sources/',
            user='0',
            detach=True,
        )

        task.logs = ''
        for log in container_output.logs(stream=True, stdout=True, stderr=True):
            task.logs += log.decode()
            task_executor.add_logs(log.decode())

        exit_code = container_output.wait()

        container_output.remove()
        
        if exit_code != 0:
            task.logs += f"\nContainer exited with error code: {exit_code}"
            if task.method.stop_on_failure:
                task.save()
                raise Exception("A mandatory task failed, stopping")
            else:
                task.status = models.Status.warning
                task.logs += f"An optional task failed, continuing anyway"
        task.save()