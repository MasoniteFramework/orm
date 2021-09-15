"""Module for miscellaneous helper methods."""

import warnings
import re


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


def database_url(url):
    regex = re.compile(
        "(?P<schema>.*?)://(?P<user>.*?):(?P<password>.*?)@(?P<host>.*?)/(?P<database>.*)"
    )
    dic = {}
    match = regex.match(url)
    user = match.group(2)
    host = match.group(4)
    hostname = host.split(":")[0]
    port = None if ":" not in host else host.split(":")[1]
    database = match.group(5)
    dic.update(
        {
            "user": user,
            "password": match.group(3),
            "host": hostname,
            "port": port,
            "database": database,
        }
    )

    return dic
