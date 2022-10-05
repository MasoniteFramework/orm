"""Module for miscellaneous helper methods."""

import warnings
import json


def is_json(json_string):
    if not isinstance(json_string, str):
        return False
    try:
        json.loads(json_string)
    except ValueError:
        return False
    return True


def deprecated(message):
    warnings.simplefilter("default", DeprecationWarning)

    def deprecated_decorator(func):
        def deprecated_func(*args, **kwargs):
            warnings.warn(
                "{} is a deprecated function. {}".format(func.__name__, message),
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return deprecated_func

    return deprecated_decorator
