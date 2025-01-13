import logging
import traceback
from . import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class BuildTaskExecutor:
    def __init__(self, buildtask: models.BuildTask):
        self.task = buildtask
        self.logs = None

    def __enter__(self):
        self.task.status = models.Status.running
        self.task.save()
        self.update_task()
        self.open_task()
        return self

    def __exit__(self, exc, value, tb):
        # self.task.refresh_from_db()
        if exc is not None:
            formated_traceback = ''.join(
                    traceback.format_exception(exc, value, tb))
            if self.task.status == models.Status.running:
                self.task.status = models.Status.failed
            if not self.task.logs:
                self.task.logs = formated_traceback
                self.add_logs(formated_traceback)
        else:
            if self.task.status == models.Status.running:
                self.task.status = models.Status.success
            self.close_task()
        self.update_task()
        self.task.save()

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

    def add_logs(self, message):
        logger.debug(message)
        self.send_socket_msg(
            {
                "type": "task",
                "action": "add_logs",
                "task": self.task.order,
                "log": message
            }
        )

    def send_socket_msg(self, event):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"logs_{self.task.build.pk}",
            event
        )