from typing import Any
from typing import Optional

from clikit.utils.string import parse_boolean
from clikit.utils.string import parse_float
from clikit.utils.string import parse_int
from clikit.utils.string import parse_string

from .abstract_option import AbstractOption


class Option(AbstractOption):
    """
    An input option
    """

    NO_VALUE = 4
    REQUIRED_VALUE = 8
    OPTIONAL_VALUE = 16
    MULTI_VALUED = 32

    STRING = 128
    BOOLEAN = 256
    INTEGER = 512
    FLOAT = 1024
    NULLABLE = 2048

    def __init__(
        self,
        long_name,
        short_name=None,
        flags=0,
        description=None,
        default=None,
        value_name="...",
    ):  # type: (str, Optional[str], int, Optional[str], Any, str) -> None
        self._validate_flags(flags)

        super(Option, self).__init__(long_name, short_name, flags, description)

        self._value_name = value_name

        if self.is_multi_valued():
            self._default = []
        else:
            self._default = None

        if self.accepts_value() or default is not None:
            self.set_default(default)

    @property
    def default(self):  # type: () -> Any
        return self._default

    @property
    def value_name(self):  # type: () -> str
        return self._value_name

    def accepts_value(self):  # type: () -> bool
        return not bool(self.NO_VALUE & self._flags)

    def parse(self, value):  # type: (Any) -> Any
        nullable = bool(self._flags & self.NULLABLE)

        if self._flags & self.BOOLEAN:
            return parse_boolean(value, nullable)
        elif self._flags & self.INTEGER:
            return parse_int(value, nullable)
        elif self._flags & self.FLOAT:
            return parse_float(value, nullable)

        return parse_string(value, nullable)

    def is_value_required(self):  # type: () -> bool
        return bool(self.REQUIRED_VALUE & self._flags)

    def is_value_optional(self):  # type: () -> bool
        return bool(self.OPTIONAL_VALUE & self._flags)

    def is_multi_valued(self):  # type: () -> bool
        return bool(self.MULTI_VALUED & self._flags)

    def set_default(self, default=None):  # type: (Any) -> None
        if not self.accepts_value():
            raise ValueError(
                "Cannot set a default value when using the flag VALUE_NONE."
            )

        if self.is_multi_valued():
            if default is None:
                default = []
            elif not isinstance(default, list):
                raise ValueError(
                    "The default value of a multi-valued option must be a list. "
                    "Got: {}".format(type(default))
                )

        self._default = default

    def _validate_flags(self, flags):  # type: (int) -> None
        super(Option, self)._validate_flags(flags)

        if flags & self.NO_VALUE:
            if flags & self.REQUIRED_VALUE:
                raise ValueError(
                    "The option flags VALUE_NONE and VALUE_REQUIRED cannot be combined."
                )

            if flags & self.OPTIONAL_VALUE:
                raise ValueError(
                    "The option flags VALUE_NONE and VALUE_OPTIONAL cannot be combined."
                )

            if flags & self.MULTI_VALUED:
                raise ValueError(
                    "The option flags VALUE_NONE and MULTI_VALUED cannot be combined."
                )

        if flags & self.OPTIONAL_VALUE and flags & self.MULTI_VALUED:
            raise ValueError(
                "The option flags VALUE_OPTIONAL and MULTI_VALUED cannot be combined."
            )

        if flags & self.STRING:
            if flags & self.BOOLEAN:
                raise ValueError(
                    "The option flags STRING and BOOLEAN cannot be combined."
                )

            if flags & self.INTEGER:
                raise ValueError(
                    "The option flags STRING and INTEGER cannot be combined."
                )

            if flags & self.FLOAT:
                raise ValueError(
                    "The option flags STRING and FLOAT cannot be combined."
                )
        elif flags & self.BOOLEAN:
            if flags & self.INTEGER:
                raise ValueError(
                    "The option flags BOOLEAN and INTEGER cannot be combined."
                )

            if flags & self.FLOAT:
                raise ValueError(
                    "The option flags BOOLEAN and FLOAT cannot be combined."
                )
        elif flags & self.INTEGER:
            if flags & self.FLOAT:
                raise ValueError(
                    "The option flags INTEGER and FLOAT cannot be combined."
                )

    def _add_default_flags(self, flags):  # type: (int) -> int
        flags = super(Option, self)._add_default_flags(flags)

        if not flags & (
            self.NO_VALUE
            | self.REQUIRED_VALUE
            | self.OPTIONAL_VALUE
            | self.MULTI_VALUED
        ):
            flags |= self.NO_VALUE

        if not flags & (self.STRING | self.BOOLEAN | self.INTEGER | self.FLOAT):
            flags |= self.STRING

        if flags & self.MULTI_VALUED and not flags & self.REQUIRED_VALUE:
            flags |= self.REQUIRED_VALUE

        return flags
