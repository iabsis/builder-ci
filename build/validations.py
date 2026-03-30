from django.core.exceptions import ValidationError


def validate_dict(value):
    if not isinstance(value, dict):
        raise ValidationError(
            "%(value)s must be a dictionnary",
            params={"value": value},
        )
    for val in value.values():
        if not isinstance(val, str):
            validate_dict(val)