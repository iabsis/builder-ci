import logging
import importlib
import traceback
from celery import Celery
from django.conf import settings
from . import models
from .step import StepAbstract
from io import StringIO as StringBuffer
from .methods import lib_get_methods, check_duplicate

app = Celery('tasks', broker='redis://localhost')
app.config_from_object("django.conf:settings", namespace="CELERY")

logger = logging.getLogger(__name__)

@app.task
def run_build(id):
    build = models.Build.objects.get(pk=id)
    build.status = models.BuildStatus.running
    build.save()

    for step in settings.STEPS_ORDER:

        one_success = False
        for module_name, method_options in lib_get_methods(step, build):
            try:
                module = importlib.import_module(module_name)
                method_instance: StepAbstract = module.Step(
                    build, method_options)
                if method_instance.is_healthy:
                    method_instance.run()
                    logger.debug(method_instance.log_contents)
                    one_success = True
                check_duplicate(build)
            except Exception as e:
                print(traceback.format_exc())
                logger.error(f"Encountered exception: {e}")
                build.status = models.BuildStatus.warning
        
        if not one_success:
            if step in settings.ONE_STEPS_MANDATORY:
                build.status = models.BuildStatus.failed
                break
            
    build.save()

