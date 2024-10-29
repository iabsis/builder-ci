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
    podman_url = settings.PODMAN_URL

    image_obj = models.Container.objects.get(pk=container_id)
    dockerfile = image_obj.render_dockerfile(**context)
    tag = image_obj.get_target_tag(**context)

    with PodmanClient(base_url=podman_url) as client:
        image, logs = client.images.build(
                    fileobj=StringIO(dockerfile),
                    tag=tag,
                    pull=True,
                )
        
        builtcontainer, _ = models.BuiltContainer.objects.get_or_create(
            name=tag,
            container=image_obj
        )

        builtcontainer.logs = "".join([json.loads(log.decode()).get('stream') for log in logs])
        builtcontainer.status = models.BuiltContainerStatus.SUCCESS
        builtcontainer.variables = context
        builtcontainer.hash = image.id
        builtcontainer.save()

