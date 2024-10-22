import logging
import importlib
from django.conf import settings
from .. import models

logger = logging.getLogger(__name__)

def lib_get_methods(step: str, build: models.Build):
    """
    Returns all expected methods based on
    build options.
    """

    # If build object contains several methods
    if isinstance(build.options.get(step), list):
        for method in build.options.get(step):
            method_name = method.get("method")
            method_options = method.get("options")
            for module in yield_load_module(step, method_name):
                yield module, method_options

    # If build object contains only one methods.
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
    """
    Return string path of  the module.
    """
    logger.debug(f"Loading method: {method} at step: {step}")
    if method == "auto":
        modules = all_step_modules(step)
        for module in modules:
            module_path = f'build.methods.{step}.{module}'
            try:
                _ = importlib.import_module(module_path)
                yield module_path
            except Exception as e:
                logger.info(f"Unable to load {module_path}: {e}")
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
    if models.Build.objects.filter(**query).count():
        build.status = models.BuildStatus.duplicate
        raise Exception("Duplicate build, not continuing")
    
