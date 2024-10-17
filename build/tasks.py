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
        for module, method_options in lib_get_methods(step, build):
            try:
                # method = importlib.import_module(f'build.methods.{step}.{module}')
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
                build.save()
        
        if not one_success:
            if step in settings.ONE_STEPS_MANDATORY:
                build.status = models.BuildStatus.warning
                build.save()
                return

def lib_get_methods(step: str, build: models.Build):
    
    if isinstance(build.options, list):
        for method in build.options.get(step):
            method_name = method.get("method")
            method_options = method.get("options")
            for module in yield_load_module(step, method_name):
                yield module, method_options

    if isinstance(build.options, dict):
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
        module = importlib.import_module(
            f'build.methods.{step}.{method}')
        yield module
    except Exception as e:
        raise Exception(
            f"Unable to load module method for step {step}: {e}")

def all_step_modules(step: str):
    try:
        return importlib.import_module(
            f'build.methods.{step}').__all__
    except Exception as e:
        raise Exception(
                f"Unable to get auto method for step {step}: {e}")
    



    # for method in extract_steps(build, step):
    #     logger.debug(f"Method name: {method_name}")
    #     if method_name == "auto":
    #         for method in importlib.import_module(f'build.methods.{step}').__all__:
    #             all_methods.append(method_name) if method_name not in all_methods else None
    #         continue
    #     all_methods.append(method_name) if method_name not in all_methods else None
    
    # for method in all_methods:
    #     try:
    #         lib = f".methods.{step}.{method}"
    #         m = importlib.import_module(lib)
    #         yield m.StepAbstract(build)
    #     except Exception as e:
    #         logger.error(f"Unable to load module {lib}: {e}")
    #         build.status = models.BuildStatus.warning
    #         if step in 
    #         raise Exception("Unable to load module on a mandatory step")

# def extract_steps(build: models.Build, step):
#     options= build.options
#     logger.debug(f"Options: {options}, Step: {step}")
#     if not options:
#         raise Exception("Unable to build without at last one option")
#     method = options.get(step)
#     if isinstance(method, dict):
#         yield method
#     if isinstance()

def check_duplicate(build: models.Build):

    query = {}
    for key in settings.DUPLICATES_ON_META:
        query[key] = getattr(build, key)
        query['status'] = models.BuildStatus.success
    if models.Build.objects.filter(**query).count() > 1:
        build.status = models.BuildStatus.duplicate
        raise Exception("Duplicate build, not continuing")