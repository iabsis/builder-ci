import re

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


validate_extended_slug = RegexValidator(
    re.compile(r'^[-a-zA-Z0-9_{}]+\Z'),
    'Enter a valid "slug" consisting of letters, numbers, underscores, hyphens, or curly braces.',
    'invalid',
)


def validate_dict(value):
    if not isinstance(value, dict):
        raise ValidationError(
            "%(value)s must be a dictionnary",
            params={"value": value},
        )
    for val in value.values():
        if not isinstance(val, str):
            validate_dict(val)