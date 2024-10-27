from django.conf import settings
from ...step import StepAbstract


class Step(StepAbstract):
    name: str = "yaml"

