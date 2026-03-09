class IgnoredException(Exception):
    """
    Exception raised when a build should be ignored rather than failed.
    This is used for situations where the build cannot proceed due to
    configuration mismatch (e.g., wrong mode for tag/branch combination)
    but it's not considered a failure.
    """
    pass
