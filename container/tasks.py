import logging
import importlib
import traceback
import json
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
    tag = f"{image_obj.name}-{image_name}-{tag_name}"

    with PodmanClient(base_url=url) as client:
        image, logs = client.images.build(
                    fileobj=StringIO(dockerfile),
                    tag=tag,
                )
        
        # logger.info(image.tags)
        # logs = []
        # for chunk in logs:
        #     if 'stream' in chunk.decode():
        #         logger.info(chunk.decode())

        builtcontainer, _ = models.BuiltContainer.objects.get_or_create(
            name=f'{tag}',
            container=image_obj
        )

        # logger.info([json.loads(log.decode()).get('stream') for log in logs])

        builtcontainer.logs = "".join([json.loads(log.decode()).get('stream') for log in logs])
        builtcontainer.status = models.BuiltContainerStatus.SUCCESS
        builtcontainer.variables = context
        builtcontainer.hash = image.id
        builtcontainer.save()