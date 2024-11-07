import logging
import importlib
import traceback
import json
from celery import Celery
from django.conf import settings
from . import models
from io import StringIO
from podman import PodmanClient
from podman.errors import BuildError

app = Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)

@app.task
def build_image(container_id: int, options: dict):

    podman_url = settings.PODMAN_URL

    image_obj = models.Container.objects.get(pk=container_id)
    dockerfile = image_obj.render_dockerfile(options=options)
    tag = image_obj.get_target_tag(options=options)

    builtcontainer, _ = models.BuiltContainer.objects.get_or_create(
        name=tag,
        container=image_obj
    )

    builtcontainer.status = models.Status.running
    builtcontainer.variables = options
    builtcontainer.save()

    try:
        with PodmanClient(base_url=podman_url) as client:
            image, logs = client.images.build(
                        fileobj=StringIO(dockerfile),
                        tag=tag,
                        pull=True,
                    )
    except BuildError as e:
        builtcontainer.logs = "".join([line.decode() for line in e.build_log])
        builtcontainer.status = models.Status.failed
        builtcontainer.save()
        return
        
    builtcontainer.logs = "".join([json.loads(log.decode()).get('stream') for log in logs])
    builtcontainer.status = models.Status.success
    
    builtcontainer.hash = image.id
    builtcontainer.save()

