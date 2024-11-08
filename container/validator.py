import re
from django.core.exceptions import ValidationError
from dockerfile_parse import DockerfileParser
from io import BytesIO

def validate_dockerfile(value):
    dockerfile = BytesIO()
    dfp = DockerfileParser(fileobj=dockerfile)
    dfp.content = value
    if not dfp.baseimage:
        raise ValidationError(f"The base image is not defined")