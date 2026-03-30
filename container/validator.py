import re
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from dockerfile_parse import DockerfileParser
from io import BytesIO

validate_extended_slug = RegexValidator(
    re.compile(r'^[-a-zA-Z0-9_{}]+\Z'),
    'Enter a valid "slug" consisting of letters, numbers, underscores, hyphens, or curly braces.',
    'invalid',
)

def validate_dockerfile(value):
    dockerfile = BytesIO()
    dfp = DockerfileParser(fileobj=dockerfile)
    dfp.content = value
    if not dfp.baseimage:
        raise ValidationError(f"The base image is not defined")