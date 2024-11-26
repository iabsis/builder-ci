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
        self.create_task()
        self.open_task()
        return self.task

    def __exit__(self, exc, value, tb):
        self.update_task()
        self.close_task()
        if exc is not None:
            if self.task.status == models.Status.running:
                self.task.status = models.Status.failed
            if not self.task.logs:
                self.task.logs = ''.join(
                    traceback.format_exception(exc, value, tb))
        else:
            self.task.status = models.Status.success
        self.task.save()

    def create_task(self):
        self.send_socket_msg(
            {
                "type": "task",
                "action": "create_task",
                "description": self.task.description,
                "task": self.task.order,
                "status": self.task.status
            }
        )

    def update_task(self):
        self.send_socket_msg(
            {
                "type": "task",
                "action": "update_task",
                "description": self.task.description,
                "task": self.task.order,
                "status": self.task.status
            }
        )

    def open_task(self):
        self.send_socket_msg(
            {
                "type": "task",
                "action": "open_task",
                "task": self.task.order
            }
        )

    def close_task(self):
        self.send_socket_msg(
            {
                "type": "task",
                "action": "close_task",
                "task": self.task.order
            }
        )

    def send_socket_msg(self, event):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"logs_{self.task.build.pk}",
            event
        )