import logging
import traceback
from . import models

logger = logging.getLogger(__name__)

class BuildTaskExecutor:
    def __init__(self, build: models.Build=None, description=None, buildtask=None, order=0):
        if not description and not buildtask:
            raise Exception("You must specify at least one of description or buildtask")
        if description:
            if not build:
                raise Exception(
                    "You must specify build with description")
            self.task = models.BuildTask.objects.create(
                description=description,
                build=build,
                order=order,
                status=models.Status.queued
            )
        else:
            self.task = buildtask
        self.logs = None

    def __enter__(self):
        self.task.status = models.Status.running
        self.task.save()
        return self.task

    def __exit__(self, exc, value, tb):
        if exc is not None:
            self.task.status = models.Status.failed
            if not self.task.logs:
                self.task.logs = ''.join(
                    traceback.format_exception(exc, value, tb))
        else:
            self.task.status = models.Status.success
        self.task.save()
