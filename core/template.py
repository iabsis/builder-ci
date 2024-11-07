from jinja2 import Template, StrictUndefined

from build.models import Build

def merged_with_default(options, default_options):
    '''
    Merge options dictionnary with default_options if defined
    '''
    if not default_options:
        return options
    for key, value in options.items():
        default_options[key] = value
    return default_options


def get_options(*, build: Build = None, options: dict = None, default_options=None):
    '''
    Returned options dictionnary based on what is defined: build or options, and default_options
    '''

    if not default_options:
        default_options = {}
    if build and options:
        raise TypeError(
            "You must provide only one of 'build' or 'options'")
    if options:
        return merged_with_default(options, default_options)
    if build:
        return merged_with_default(
            build.request.computed_options, default_options)
    return default_options

def get_template(template, *, build: Build = None, options: dict = None, default_options=None):
    '''
    Return rendered templated based on what is defined: build or options, and default_options
    '''
    opt = get_options(build=build, options=options, default_options=default_options)
    t = Template(template, undefined=StrictUndefined)
    return t.render(**opt).replace('\r', '')
