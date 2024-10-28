from django.core.exceptions import ValidationError
import regex

def validate_regex_pattern(value):
    """
    Validates that the input is a valid regular expression pattern.
    Uses the 'regex' module to support timeouts.
    """
    try:
        regex.compile(value)
    except regex.error as e:
        raise ValidationError(f"Invalid regular expression: {e}")
