from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from .format.args_format import ArgsFormat
from .raw_args import RawArgs


class Args(object):
    """
    The parsed console arguments.
    """

    def __init__(self, fmt, raw_args=None):  # type: (ArgsFormat, RawArgs) -> None
        self._fmt = fmt
        self._raw_args = raw_args
        self._options = {}
        self._arguments = {}

    @property
    def format(self):  # type: () -> ArgsFormat
        return self._fmt

    @property
    def raw_args(self):  # type: () -> RawArgs
        return self._raw_args

    @property
    def script_name(self):  # type: () -> Optional[str]
        if self._raw_args:
            return self._raw_args.script_name

    @property
    def command_names(self):
        return self._fmt.get_command_names()

    @property
    def command_options(self):
        return self._fmt.get_command_options()

    def option(self, name):
        option = self._fmt.get_option(name)

        if option.long_name in self._options:
            return self._options[option.long_name]

        if option.accepts_value():
            return option.default

        return False

    def options(self, include_defaults=True):
        options = self._options.copy()

        if include_defaults:
            for option in self._fmt.get_options().values():
                name = option.long_name

                if not name in options:
                    default = False
                    if option.accepts_value():
                        default = option.default

                    options[name] = default

        return options

    def set_option(self, name, value=True):
        option = self._fmt.get_option(name)

        if option.is_multi_valued():
            if not isinstance(value, list):
                value = [value]

            for i, v in enumerate(value):
                value[i] = option.parse(v)
        elif option.accepts_value():
            value = option.parse(value)
        elif value is False:
            if option.long_name in self._options:
                del self._options[option.long_name]

            return self
        else:
            value = True

        self._options[option.long_name] = value

        return self

    def is_option_set(self, name):  # type: (str) -> bool
        return name in self._options

    def is_option_defined(self, name):  # type: (str) -> bool
        return self._fmt.has_option(name)

    def argument(self, name):  # type: (Union[str, int]) -> Any
        argument = self._fmt.get_argument(name)

        if argument.name in self._arguments:
            return self._arguments[name]

        return argument.default

    def arguments(self, include_defaults=True):  # type: (bool) -> Dict[str, Any]
        arguments = {}

        for argument in self._fmt.get_arguments().values():
            name = argument.name

            if name in self._arguments:
                arguments[name] = self._arguments[name]
            elif include_defaults:
                arguments[name] = argument.default

        return arguments

    def set_argument(self, name, value):  # type: (Union[str, int], Any) -> Args
        argument = self._fmt.get_argument(name)

        if argument.is_multi_valued():
            if not isinstance(value, list):
                value = [value]

            for i, v in enumerate(value):
                value[i] = argument.parse(v)
        else:
            value = argument.parse(value)

        self._arguments[argument.name] = value

        return self

    def is_argument_set(self, name):  # type: (Union[str, int]) -> bool
        return name in self._arguments

    def is_argument_defined(self, name):  # type: (Union[str, int]) -> bool
        return self._fmt.has_argument(name)
