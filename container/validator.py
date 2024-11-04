import re
from django.core.exceptions import ValidationError
from dockerfile_parse import DockerfileParser

def validate_dockerfile(value):
    dfp = DockerfileParser()
    dfp.content = value
    if not dfp.baseimage:
        raise ValidationError(f"The base image is not defined")