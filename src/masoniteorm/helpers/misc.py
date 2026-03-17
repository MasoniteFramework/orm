"""Module for miscellaneous helper methods."""

import warnings


def deprecated(message):
    warnings.simplefilter("default", DeprecationWarning)

    def deprecated_decorator(func):
        def deprecated_func(*args, **kwargs):
            warnings.warn(
                f"{func.__name__} is a deprecated function. {message}",
                category=DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return deprecated_func

    return deprecated_decorator
