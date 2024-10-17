import logging
import importlib
import traceback
from celery import Celery
from django.conf import settings
from . import models
from .step import StepAbstract

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


def lib_get_methods(step: str, build: models.Build):

    
    if isinstance(build.options.get(step), list):
        for method in build.options.get(step):
            method_name = method.get("method")
            method_options = method.get("options")
            for module in yield_load_module(step, method_name):
                yield module, method_options

    if isinstance(build.options.get(step), dict):
        logger.debug(f"Option type: {build.options.get(step)}")
        logger.debug(f"Options: {type(build.options.get(step))}")
        if build.options.get(step):
            method_name = build.options.get(step).get("method")
            method_options = build.options.get(step).get("options")
            for module in yield_load_module(step, method_name):
                yield module, method_options
        else:
            for module in yield_load_module(step, 'auto'):
                yield module, method_options

def yield_load_module(step: str, method: str):
    logger.debug(f"Loading method: {method} at step: {step}")
    if method == "auto":
        modules = all_step_modules(step)
        for module in modules:
            yield module
        return

    try:
        module = f'build.methods.{step}.{method}'
        yield module
    except Exception as e:
        raise Exception(
            f"Unable to load module method for step {step}: {e}")

def all_step_modules(step: str) -> list:
    try:
        return importlib.import_module(
            f'build.methods.{step}').__all__
    except Exception as e:
        logger.warning(
                f"Unable to get auto method for step {step}: {e}")
        return []


def check_duplicate(build: models.Build):

    query = {}
    for key in settings.DUPLICATES_ON_META:
        query[key] = getattr(build, key)
        query['status'] = models.BuildStatus.success
    if models.Build.objects.filter(**query).count() > 1:
        build.status = models.BuildStatus.duplicate
        raise Exception("Duplicate build, not continuing")