import logging
import traceback
from . import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class BuildTaskExecutor:
    def __init__(self, build: models.Build=None, description=None, buildtask=None):
        if not description and not buildtask:
            raise Exception("You must specify at least one of description or buildtask")
        if description:
            if not build:
                raise Exception(
                    "You must specify build with description")
            self.task = models.BuildTask.objects.create(
                description=description,
                build=build,
                status=models.Status.queued
            )
        else:
            self.task = buildtask
        self.logs = None

    def __enter__(self):
        self.task.status = models.Status.running
        self.task.save()
        self.send_socket_msg(f"Running: {self.task.description}")
        return self.task

    def __exit__(self, exc, value, tb):
        self.send_socket_msg(f"Finished: {self.task.description}")
        if exc is not None:
            if self.task.status == models.Status.running:
                self.task.status = models.Status.failed
            if not self.task.logs:
                self.task.logs = ''.join(
                    traceback.format_exception(exc, value, tb))
        else:
            self.task.status = models.Status.success
        self.task.save()

    def send_socket_msg(self, message):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"logs_{self.task.build.pk}",
            {
                "type": "log_message",
                "message": message,
            }
        )