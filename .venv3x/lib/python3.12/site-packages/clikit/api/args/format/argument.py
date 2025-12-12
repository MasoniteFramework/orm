import re

from typing import Any
from typing import Optional

from clikit.utils._compat import basestring
from clikit.utils.string import parse_boolean
from clikit.utils.string import parse_float
from clikit.utils.string import parse_int
from clikit.utils.string import parse_string


class Argument(object):
    """
    An input argument.
    """

    REQUIRED = 1
    OPTIONAL = 2
    MULTI_VALUED = 4
    STRING = 16
    BOOLEAN = 32
    INTEGER = 64
    FLOAT = 128
    NULLABLE = 256

    def __init__(
        self, name, flags=0, description=None, default=None
    ):  # type: (str, int, Optional[str], Any) -> None
        if not isinstance(name, basestring):
            raise ValueError(
                "The argument name must be a string. Got: {}".format(type(name))
            )

        if not name:
            raise ValueError("The argument name must not be empty.")

        if not name[:1].isalpha():
            raise ValueError("The argument name must start with a letter")

        if not re.match(r"^[a-zA-Z0-9\-]+$", name):
            raise ValueError(
                "The argument name must contain letters, digits and hyphens only."
            )

        if description is not None:
            if not isinstance(description, basestring):
                raise ValueError(
                    "The argument description must be a string. Got: {}".format(
                        type(description)
                    )
                )

            if not description:
                raise ValueError("The argument description must not be empty.")

        self._validate_flags(flags)

        flags = self._add_default_flags(flags)

        self._name = name
        self._flags = flags
        self._description = description

        if self.is_multi_valued():
            self._default = []
        else:
            self._default = None

        if self.is_optional() or default is not None:
            self.set_default(default)

    @property
    def name(self):  # type: () -> str
        return self._name

    @property
    def flags(self):  # type: () -> int
        return self._flags

    @property
    def description(self):  # type: () -> Optional[str]
        return self._description

    @property
    def default(self):  # type: () -> Any
        return self._default

    def is_required(self):  # type: () -> bool
        return bool(self.REQUIRED & self._flags)

    def is_optional(self):  # type: () -> bool
        return bool(self.OPTIONAL & self._flags)

    def is_multi_valued(self):  # type: () -> bool
        return bool(self.MULTI_VALUED & self._flags)

    def set_default(self, default=None):  # type: (Any) -> None
        if self.is_required():
            raise ValueError("Required arguments do not accept default values.")

        if self.is_multi_valued():
            if default is None:
                default = []
            elif not isinstance(default, list):
                raise ValueError(
                    "The default value of a multi-valued argument must be a list. "
                    "Got: {}".format(type(default))
                )

        self._default = default

    def parse(self, value):  # type: (Any) -> Any
        nullable = bool(self._flags & self.NULLABLE)

        if self._flags & self.BOOLEAN:
            return parse_boolean(value, nullable)
        elif self._flags & self.INTEGER:
            return parse_int(value, nullable)
        elif self._flags & self.FLOAT:
            return parse_float(value, nullable)

        return parse_string(value, nullable)

    def _validate_flags(self, flags):  # type: (int) -> None
        if flags & self.REQUIRED and flags & self.OPTIONAL:
            raise ValueError(
                "The argument flags REQUIRED and OPTIONAL cannot be combined."
            )

        if flags & self.STRING:
            if flags & self.BOOLEAN:
                raise ValueError(
                    "The argument flags STRING and BOOLEAN cannot be combined."
                )

            if flags & self.INTEGER:
                raise ValueError(
                    "The argument flags STRING and INTEGER cannot be combined."
                )

            if flags & self.FLOAT:
                raise ValueError(
                    "The argument flags STRING and FLOAT cannot be combined."
                )
        elif flags & self.BOOLEAN:
            if flags & self.INTEGER:
                raise ValueError(
                    "The argument flags BOOLEAN and INTEGER cannot be combined."
                )

            if flags & self.FLOAT:
                raise ValueError(
                    "The argument flags BOOLEAN and FLOAT cannot be combined."
                )
        elif flags & self.INTEGER:
            if flags & self.FLOAT:
                raise ValueError(
                    "The argument flags INTEGER and FLOAT cannot be combined."
                )

    def _add_default_flags(self, flags):  # type: (int) -> int
        if not flags & (self.REQUIRED | self.OPTIONAL):
            flags |= self.OPTIONAL

        if not flags & (self.STRING | self.BOOLEAN | self.INTEGER | self.FLOAT):
            flags |= self.STRING

        return flags
