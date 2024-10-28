import logging
import importlib
import traceback
from celery import Celery
from django.conf import settings
from . import models
from io import StringIO
from podman import PodmanClient

app = Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)

@app.task
def build_image(container_id, **context):
    # url = "unix:///run/podman/podman.sock"
    url = "unix:///run/user/1000/podman/podman.sock"

    image_name = context.get('image')
    tag_name = context.get('tag')

    if not image_name or not tag_name:
        raise Exception("The key image and codename are mandatory")

    image_obj = models.Container.objects.get(pk=container_id)
    dockerfile = image_obj.render_dockerfile(**context)

    with PodmanClient(base_url=url) as client:
        client.images.build(
                    fileobj=StringIO(dockerfile),
                    tag=f"{image_obj.name}-{image_name}-{tag_name}",
                )