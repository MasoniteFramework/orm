import re

from typing import Any
from typing import Optional

from ._compat import basestring


def parse_string(value, nullable=True):  # type: (Any, bool) -> Optional[str]
    if nullable and (value is None or value == "null"):
        return

    if value is None:
        return "null"

    if isinstance(value, bool):
        return str(value).lower()

    return str(value)


def parse_boolean(value, nullable=True):  # type: (Any, bool) -> Optional[bool]
    if nullable and (value is None or value == "null"):
        return

    if isinstance(value, bool):
        return value

    if isinstance(value, int):
        value = str(value)

    if isinstance(value, basestring):
        if not value:
            return False

        if value in {"false", "0", "no", "off"}:
            return False

        if value in {"true", "1", "yes", "on"}:
            return True

    raise ValueError('The value "{}" cannot be parsed as boolean.'.format(value))


def parse_int(value, nullable=True):  # type: (Any, bool) -> Optional[int]
    if nullable and (value is None or value == "null"):
        return

    try:
        return int(value)
    except ValueError:
        raise ValueError('The value "{}" cannot be parsed as integer.'.format(value))


def parse_float(value, nullable=True):  # type: (Any, bool) -> Optional[float]
    if nullable and (value is None or value == "null"):
        return

    try:
        return float(value)
    except ValueError:
        raise ValueError('The value "{}" cannot be parsed as float.'.format(value))


def get_string_length(
    string, formatter=None
):  # type: (str, Optional[Formatter]) -> int
    if formatter is not None:
        string = formatter.remove_format(string)

    return len(string)


def get_max_word_length(
    string, formatter=None
):  # type: (str, Optional[Formatter]) -> int
    if formatter is not None:
        string = formatter.remove_format(string)

    max_length = 0
    words = re.split("\s+", string)

    for word in words:
        max_length = max(max_length, get_string_length(word))

    return max_length


def get_max_line_length(
    string, formatter=None
):  # type: (str, Optional[Formatter]) -> int
    if formatter is not None:
        string = formatter.remove_format(string)

    max_length = 0
    words = re.split("\n", string)

    for word in words:
        max_length = max(max_length, get_string_length(word))

    return max_length
