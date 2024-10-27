from django.conf import settings
from ...step import StepAbstract

from configparser import ConfigParser


class Step(StepAbstract):
    name: str = "ini"

    def __init__(self, build, options):
        super().__init__(build, options)
    
        self.config = ConfigParser()
        self.config.read(settings.CONFIG_LOCATION)

