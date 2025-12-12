from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from ..exceptions import NoSuchArgumentException
from ..exceptions import NoSuchOptionException

from .argument import Argument
from .option import Option
from .command_name import CommandName
from .command_option import CommandOption


class ArgsFormat(object):
    """
    The format used to parse a RawArgs instance.
    """

    def __init__(
        self, elements=None, base_format=None
    ):  # type: (Optional[Union[List[Any], ArgsFormatBuilder]], Optional[ArgsFormat])
        from .args_format_builder import ArgsFormatBuilder

        if elements is None:
            elements = []

        if isinstance(elements, ArgsFormatBuilder):
            builder = elements
        else:
            builder = self._create_builder_for_elements(elements)

        if base_format is None:
            base_format = builder.base_format

        self._base_format = base_format
        self._command_names = builder.get_command_names(False)
        self._command_options = {}
        self._command_options_by_short_name = {}
        self._arguments = builder.get_arguments(False)
        self._options = builder.get_options(False)
        self._options_by_short_name = {}
        self._has_multi_valued_arg = builder.has_multi_valued_argument(False)
        self._hash_optional_arg = builder.has_optional_argument(False)

        for option in self._options.values():
            if option.short_name:
                self._options_by_short_name[option.short_name] = option

        for command_option in builder.get_command_options():
            self._command_options[command_option.long_name] = command_option

            if command_option.short_name:
                self._command_options_by_short_name[
                    command_option.short_name
                ] = command_option

            for long_alias in command_option.long_aliases:
                self._command_options[long_alias] = command_option

            for short_alias in command_option.short_aliases:
                self._command_options_by_short_name[short_alias] = command_option

    @property
    def base_format(self):  # type: () -> ArgsFormat
        return self._base_format

    def has_command_names(self, include_base=True):  # type: (bool) -> bool
        if self._command_names:
            return True

        if include_base and self._base_format:
            return self._base_format.has_command_names()

        return False

    def get_command_names(self, include_base=True):  # type: (bool) -> List[CommandName]
        command_names = self._command_names

        if include_base and self._base_format:
            command_names = self._base_format.get_command_names() + command_names

        return command_names

    def has_command_option(self, name, include_base=True):  # type: (str, bool) -> bool
        if name in self._command_options or name in self._command_options_by_short_name:
            return True

        if include_base and self._base_format:
            return self._base_format.has_command_option(name)

        return False

    def has_command_options(self, include_base=True):  # type: (bool) -> bool
        if self._command_options:
            return True

        if include_base and self._base_format:
            return self._base_format.has_command_options()

        return False

    def get_command_option(
        self, name, include_base=True
    ):  # type: (str, bool) -> CommandOption
        if name in self._command_options:
            return self._command_options[name]

        if name in self._command_options_by_short_name:
            return self._command_options_by_short_name[name]

        if include_base and self._base_format:
            return self._base_format.get_command_option(name)

        raise NoSuchOptionException(name)

    def get_command_options(
        self, include_base=True
    ):  # type: (bool) -> List[CommandOption]
        command_options = list(self._command_options.values())

        if include_base and self._base_format:
            command_options += self._base_format.get_command_options()

        return command_options

    def has_argument(
        self, name, include_base=True
    ):  # type: (Union[str, int], bool) -> bool
        arguments = self.get_arguments(include_base)

        if isinstance(name, int):
            return name < len(arguments)

        return name in arguments

    def has_multi_valued_argument(self, include_base=True):  # type: (bool) -> bool
        if self._has_multi_valued_arg:
            return True

        if include_base and self._base_format:
            return self._base_format.has_multi_valued_argument()

        return False

    def has_optional_argument(self, include_base=True):  # type: (bool) -> bool
        if self._hash_optional_arg:
            return True

        if include_base and self._base_format:
            return self._base_format.has_optional_argument()

        return False

    def has_required_argument(self, include_base=True):  # type: (bool) -> bool
        if not self._hash_optional_arg and self._arguments:
            return True

        if include_base and self._base_format:
            return self._base_format.has_required_argument()

        return False

    def has_arguments(self, include_base=True):  # type: (bool) -> bool
        if self._arguments:
            return True

        if include_base and self._base_format:
            return self._base_format.has_arguments()

        return False

    def get_argument(
        self, name, include_base=True
    ):  # type: (Union[str, int], bool) -> Argument
        if isinstance(name, int):
            arguments = list(self.get_arguments(include_base).values())

            if name >= len(arguments):
                raise NoSuchArgumentException(name)
        else:
            arguments = self.get_arguments(include_base)

            if name not in arguments:
                raise NoSuchArgumentException(name)

        return arguments[name]

    def get_arguments(self, include_base=True):  # type: (bool) -> Dict[str, Argument]
        arguments = self._arguments.copy()

        if include_base and self._base_format:
            base_arguments = self._base_format.get_arguments()
            base_arguments.update(arguments)
            arguments = base_arguments

        return arguments

    def has_option(self, name, include_base=True):  # type: (str, bool) -> bool
        if name in self._options or name in self._options_by_short_name:
            return True

        if include_base and self._base_format:
            return self._base_format.has_option(name)

        return False

    def has_options(self, include_base=True):  # type: (bool) -> bool
        if self._options:
            return True

        if include_base and self._base_format:
            return self._base_format.has_options()

        return False

    def get_option(self, name, include_base=True):  # type: (str, bool) -> Option
        if name in self._options:
            return self._options[name]

        if name in self._options_by_short_name:
            return self._options_by_short_name[name]

        if include_base and self._base_format:
            return self._base_format.get_option(name)

        raise NoSuchOptionException(name)

    def get_options(self, include_base=True):  # type: (bool) -> Dict[str, Option]
        options = self._options.copy()

        if include_base and self._base_format:
            options.update(self._base_format.get_options())

        return options

    def _create_builder_for_elements(
        self, elements, base_format=None
    ):  # type: (List[Any], Optional[ArgsFormat]) -> ArgsFormatBuilder
        from .args_format_builder import ArgsFormatBuilder

        builder = ArgsFormatBuilder(base_format)

        for element in elements:
            if isinstance(element, CommandName):
                builder.add_command_name(element)
            elif isinstance(element, CommandOption):
                builder.add_command_option(element)
            elif isinstance(element, Option):
                builder.add_option(element)
            elif isinstance(element, Argument):
                builder.add_argument(element)

        return builder
