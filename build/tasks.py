import logging
from celery import Celery


app = Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)


@app.task
def run_build(id):
    print(id)
    pass
